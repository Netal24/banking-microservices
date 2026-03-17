import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from decimal import Decimal, ROUND_HALF_UP
from common.db import get_session
from common.redis_client import get_redis
from common.rabbit import publish_event
from . import models, schemas

router = APIRouter(prefix="/transaction", tags=["Transaction Service"])
RATE_LIMIT = 5
FRAUD_THRESHOLD = 100_000_00

def to_cents(amount: float) -> int:
    return int(Decimal(str(amount)).scaleb(2).to_integral_value(rounding=ROUND_HALF_UP))

async def rate_limit(user_id: int, action: str = "transfer"):
    redis = await get_redis()
    key = f"rl:{action}:{user_id}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 60)
    if count > RATE_LIMIT:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded: max {RATE_LIMIT} per minute")

async def bust_cache(account_id: int):
    redis = await get_redis()
    await redis.delete(f"balance:{account_id}")

@router.post("/transfer", response_model=schemas.TransactionResponse)
async def transfer(req: schemas.TransferRequest, session: Session = Depends(get_session)):
    await rate_limit(req.user_id)
    amount_cents = to_cents(req.amount)
    src = session.exec(select(models.Account).where(models.Account.id == req.source_account_id).with_for_update()).first()
    dst = session.exec(select(models.Account).where(models.Account.id == req.destination_account_id).with_for_update()).first()
    if not src or not dst:
        raise HTTPException(status_code=404, detail="Account not found")
    if src.balance_cents < amount_cents:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    txn_status = "flagged" if amount_cents > FRAUD_THRESHOLD else "completed"
    src.balance_cents -= amount_cents
    dst.balance_cents += amount_cents
    txn = models.Transaction(source_account_id=src.id, destination_account_id=dst.id, amount_cents=amount_cents, currency=req.currency.upper(), transaction_type="transfer", status=txn_status, reference=req.reference)
    session.add_all([src, dst, txn])
    session.commit()
    session.refresh(txn)
    await bust_cache(src.id)
    await bust_cache(dst.id)
    await publish_event("transactions", "transaction.completed", {"transaction_id": txn.id, "source_account_id": src.id, "destination_account_id": dst.id, "amount_cents": amount_cents, "currency": req.currency.upper(), "status": txn_status, "user_id": req.user_id, "transaction_type": "transfer"})
    return schemas.TransactionResponse(transaction_id=txn.id, status=txn_status, message=f"Transfer of {req.currency} {req.amount:.2f} {txn_status}")

@router.post("/deposit", response_model=schemas.TransactionResponse)
async def deposit(req: schemas.DepositRequest, session: Session = Depends(get_session)):
    acc = session.exec(select(models.Account).where(models.Account.id == req.account_id).with_for_update()).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    amount_cents = to_cents(req.amount)
    acc.balance_cents += amount_cents
    txn = models.Transaction(source_account_id=0, destination_account_id=req.account_id, amount_cents=amount_cents, currency=req.currency.upper(), transaction_type="deposit", status="completed", reference=req.reference)
    session.add_all([acc, txn])
    session.commit()
    session.refresh(txn)
    await bust_cache(req.account_id)
    await publish_event("transactions", "transaction.completed", {"transaction_id": txn.id, "destination_account_id": req.account_id, "amount_cents": amount_cents, "currency": req.currency.upper(), "status": "completed", "transaction_type": "deposit"})
    return schemas.TransactionResponse(transaction_id=txn.id, status="completed", message=f"Deposited {req.currency} {req.amount:.2f}")

@router.post("/withdraw", response_model=schemas.TransactionResponse)
async def withdraw(req: schemas.WithdrawRequest, session: Session = Depends(get_session)):
    await rate_limit(req.user_id, "withdraw")
    acc = session.exec(select(models.Account).where(models.Account.id == req.account_id).with_for_update()).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    amount_cents = to_cents(req.amount)
    if acc.balance_cents < amount_cents:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    acc.balance_cents -= amount_cents
    txn = models.Transaction(source_account_id=req.account_id, destination_account_id=0, amount_cents=amount_cents, currency=req.currency.upper(), transaction_type="withdrawal", status="completed", reference=req.reference)
    session.add_all([acc, txn])
    session.commit()
    session.refresh(txn)
    await bust_cache(req.account_id)
    await publish_event("transactions", "transaction.completed", {"transaction_id": txn.id, "source_account_id": req.account_id, "amount_cents": amount_cents, "currency": req.currency.upper(), "status": "completed", "transaction_type": "withdrawal"})
    return schemas.TransactionResponse(transaction_id=txn.id, status="completed", message=f"Withdrew {req.currency} {req.amount:.2f}")

@router.get("/history/{account_id}", response_model=list[schemas.TransactionRead])
def history(account_id: int, limit: int = Query(default=20, le=100), offset: int = 0, session: Session = Depends(get_session)):
    return session.exec(select(models.Transaction).where((models.Transaction.source_account_id == account_id) | (models.Transaction.destination_account_id == account_id)).order_by(models.Transaction.created_at.desc()).offset(offset).limit(limit)).all()
