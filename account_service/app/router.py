import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from common.db import get_session
from common.redis_client import get_redis
from . import models, schemas

router = APIRouter(prefix="/account", tags=["Account Service"])
CACHE_TTL = 30

@router.post("/create", response_model=schemas.AccountRead, status_code=201)
def create_account(acc_in: schemas.AccountCreate, session: Session = Depends(get_session)):
    acc = models.Account(owner_id=acc_in.owner_id, currency=acc_in.currency.upper(), account_type=acc_in.account_type)
    session.add(acc)
    session.commit()
    session.refresh(acc)
    return acc

@router.get("/{account_id}", response_model=schemas.AccountRead)
def get_account(account_id: int, session: Session = Depends(get_session)):
    acc = session.get(models.Account, account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return acc

@router.get("/{account_id}/balance", response_model=schemas.BalanceRead)
async def get_balance(account_id: int, session: Session = Depends(get_session)):
    redis = await get_redis()
    cached = await redis.get(f"balance:{account_id}")
    if cached:
        return schemas.BalanceRead(**json.loads(cached))
    acc = session.get(models.Account, account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    data = schemas.BalanceRead(account_id=acc.id, account_number=acc.account_number, balance=round(acc.balance_cents / 100.0, 2), currency=acc.currency)
    await redis.setex(f"balance:{account_id}", CACHE_TTL, json.dumps(data.model_dump()))
    return data

@router.get("/owner/{owner_id}", response_model=list[schemas.AccountRead])
def list_accounts(owner_id: int, session: Session = Depends(get_session)):
    return session.exec(select(models.Account).where(models.Account.owner_id == owner_id)).all()
