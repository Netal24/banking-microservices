import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Optional

MAX_AMOUNT_CENTS = 100_000_00
MAX_PER_MINUTE = 3
MAX_PER_HOUR = 10

@dataclass
class FraudContext:
    transaction_id: int
    source_account_id: int
    destination_account_id: int
    amount_cents: int
    currency: str
    transaction_type: str
    user_id: Optional[int] = None

_1m: dict = defaultdict(deque)
_1h: dict = defaultdict(deque)

def _prune(dq, secs):
    now = time.time()
    while dq and now - dq[0] > secs:
        dq.popleft()

def rule_high_amount(ctx):
    if ctx.amount_cents > MAX_AMOUNT_CENTS:
        return True, f"Amount ₹{ctx.amount_cents/100:,.2f} exceeds limit"
    return False, ""

def rule_rapid_1m(ctx):
    dq = _1m[ctx.source_account_id]
    _prune(dq, 60)
    dq.append(time.time())
    if len(dq) > MAX_PER_MINUTE:
        return True, f"{len(dq)} transfers in 60 seconds"
    return False, ""

def rule_rapid_1h(ctx):
    dq = _1h[ctx.source_account_id]
    _prune(dq, 3600)
    dq.append(time.time())
    if len(dq) > MAX_PER_HOUR:
        return True, f"{len(dq)} transfers in 1 hour"
    return False, ""

def rule_odd_hours(ctx):
    h = time.localtime().tm_hour
    if 0 <= h < 5:
        return True, f"Transaction at odd hour {h:02d}:xx"
    return False, ""

ALL_RULES = [rule_high_amount, rule_rapid_1m, rule_rapid_1h, rule_odd_hours]

def evaluate(ctx: FraudContext) -> list[str]:
    return [reason for rule in ALL_RULES for triggered, reason in [rule(ctx)] if triggered]
