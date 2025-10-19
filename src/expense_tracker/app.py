from contextlib import asynccontextmanager
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field as SQLField, create_engine, Session, select
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# ---------- DB MODELS ----------
class Group(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    name: str

class GroupMember(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    group_id: int
    user_id: str

class Expense(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    group_id: int
    payer_id: str
    amount: float
    description: Optional[str] = None
    date: str
    split_type: str  # "equal" | "shares" | "percent"

class ExpenseSplit(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    expense_id: int
    user_id: str
    share_value: float  # meaning depends on split_type
    owed_amount: float  # computed by server

class Settlement(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    group_id: int
    from_user_id: str
    to_user_id: str
    amount: float
    date: str
    note: Optional[str] = None

ENGINE = create_engine("sqlite:///./dev.db", echo=False)
def init_db():
    SQLModel.metadata.create_all(ENGINE)

# ---------- SCHEMAS ----------
class GroupCreate(BaseModel):
    name: str
    members: List[str] = Field(default_factory=list)

class GroupRead(BaseModel):
    id: int
    name: str
    members: List[str]

class SplitInput(BaseModel):
    user_id: str
    share_value: Optional[float] = None  # needed for shares/percent

class ExpenseCreate(BaseModel):
    payer_id: str
    amount: float = Field(gt=0)
    description: Optional[str] = None
    date: str
    split_type: str = Field(pattern="^(equal|shares|percent)$")
    splits: List[SplitInput]

class ExpenseRead(BaseModel):
    id: int
    payer_id: str
    amount: float
    description: Optional[str]
    date: str
    split_type: str

class SettlementCreate(BaseModel):
    from_user_id: str
    to_user_id: str
    amount: float = Field(gt=0)
    date: str
    note: Optional[str] = None

class BalanceRead(BaseModel):
    balances: Dict[str, float]     # + gets, - owes
    suggestions: List[Dict] = []   # optional simplified payouts

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()          # <-- your existing function
    yield

# ---------- APP ----------
app = FastAPI(title="Group Expense Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # dev only; in prod set to ["https://your-frontend.domain"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# helpers
def get_members(s: Session, gid: int) -> List[str]:
    stmt = select(GroupMember).where(GroupMember.group_id == gid)
    return [m.user_id for m in s.exec(stmt).all()]

def ensure_members(s: Session, gid: int, users: List[str]):
    members = set(get_members(s, gid))
    missing = [u for u in users if u not in members]
    if missing:
        raise HTTPException(400, detail=f"Users not in group: {missing}")

def compute_balances(s: Session, gid: int) -> Dict[str, float]:
    balances: Dict[str, float] = {u: 0.0 for u in get_members(s, gid)}
    # expenses
    ex_stmt = select(Expense).where(Expense.group_id == gid)
    expenses = s.exec(ex_stmt).all()
    for ex in expenses:
        balances[ex.payer_id] = balances.get(ex.payer_id, 0.0) + ex.amount
        sp_stmt = select(ExpenseSplit).where(ExpenseSplit.expense_id == ex.id)
        for sp in s.exec(sp_stmt).all():
            balances[sp.user_id] = balances.get(sp.user_id, 0.0) - sp.owed_amount
    # settlements
    st_stmt = select(Settlement).where(Settlement.group_id == gid)
    for st in s.exec(st_stmt).all():
        balances[st.from_user_id] = balances.get(st.from_user_id, 0.0) - st.amount
        balances[st.to_user_id]   = balances.get(st.to_user_id, 0.0) + st.amount
    # round to 2 decimals
    return {u: round(v, 2) for u, v in balances.items()}

def normalize_splits(amount: float, split_type: str, members: List[str], splits: List[SplitInput]) -> List[ExpenseSplit]:
    if split_type == "equal":
        users = [sp.user_id for sp in splits] or members
        n = len(users)
        if n == 0:
            raise HTTPException(400, detail="No users provided for equal split")
        each = round(amount / n, 2)
        # fix rounding to sum exactly
        owed = [each] * n
        delta = round(amount - sum(owed), 2)
        if delta != 0:
            owed[0] = round(owed[0] + delta, 2)
        return [ExpenseSplit(expense_id=0, user_id=u, share_value=1.0, owed_amount=o) for u, o in zip(users, owed)]

    if split_type == "shares":
        if not splits:
            raise HTTPException(400, detail="shares requires splits with share_value")
        total = sum((sp.share_value or 0) for sp in splits)
        if total <= 0:
            raise HTTPException(400, detail="sum of shares must be > 0")
        result = []
        acc = 0.0
        for i, sp in enumerate(splits):
            owed = round(amount * (sp.share_value / total), 2)
            acc += owed
            result.append((sp.user_id, sp.share_value, owed))
        # rounding fix
        delta = round(amount - acc, 2)
        if delta != 0 and result:
            user, sv, owed = result[0]
            result[0] = (user, sv, round(owed + delta, 2))
        return [ExpenseSplit(expense_id=0, user_id=u, share_value=sv, owed_amount=o) for u, sv, o in result]

    if split_type == "percent":
        if not splits:
            raise HTTPException(400, detail="percent requires splits with share_value=percent")
        total = round(sum((sp.share_value or 0) for sp in splits), 2)
        if abs(total - 100.0) > 0.01:
            raise HTTPException(400, detail="sum of percents must be 100")
        result = []
        acc = 0.0
        for sp in splits:
            owed = round(amount * (sp.share_value / 100.0), 2)
            acc += owed
            result.append((sp.user_id, sp.share_value, owed))
        delta = round(amount - acc, 2)
        if delta != 0 and result:
            user, sv, owed = result[0]
            result[0] = (user, sv, round(owed + delta, 2))
        return [ExpenseSplit(expense_id=0, user_id=u, share_value=sv, owed_amount=o) for u, sv, o in result]

    raise HTTPException(400, detail="invalid split_type")

# ---------- API ROUTES ----------
@app.post("/groups/", response_model=GroupRead)
def create_group(payload: GroupCreate):
    if not payload.name.strip():
        raise HTTPException(400, detail="group name required")
    with Session(ENGINE) as s:
        g = Group(name=payload.name.strip())
        s.add(g)
        s.commit()
        s.refresh(g)
        for u in payload.members:
            s.add(GroupMember(group_id=g.id, user_id=u))
        s.commit()
        members = get_members(s, g.id)
        return GroupRead(id=g.id, name=g.name, members=members)

@app.get("/groups/{gid}", response_model=GroupRead)
def get_group(gid: int):
    with Session(ENGINE) as s:
        g = s.get(Group, gid)
        if not g:
            raise HTTPException(404, detail="group not found")
        return GroupRead(id=g.id, name=g.name, members=get_members(s, gid))

@app.post("/groups/{gid}/expenses", response_model=ExpenseRead)
def add_expense(gid: int, payload: ExpenseCreate):
    if payload.amount <= 0:
        raise HTTPException(400, detail="amount must be > 0")
    with Session(ENGINE) as s:
        g = s.get(Group, gid)
        if not g:
            raise HTTPException(404, detail="group not found")
        members = get_members(s, gid)
        # ensure payer & all split users are members
        ensure_members(s, gid, [payload.payer_id] + [sp.user_id for sp in payload.splits])
        # normalize splits
        norm = normalize_splits(payload.amount, payload.split_type, members, payload.splits)
        # create expense
        ex = Expense(group_id=gid, payer_id=payload.payer_id, amount=payload.amount,
                     description=payload.description, date=payload.date, split_type=payload.split_type)
        s.add(ex); s.commit(); s.refresh(ex)
        # persist splits
        for sp in norm:
            sp.expense_id = ex.id
            s.add(sp)
        s.commit()
        return ExpenseRead(id=ex.id, payer_id=ex.payer_id, amount=ex.amount,
                           description=ex.description, date=ex.date, split_type=ex.split_type)

@app.get("/groups/{gid}/expenses", response_model=List[ExpenseRead])
def list_expenses(gid: int):
    with Session(ENGINE) as s:
        if not s.get(Group, gid):
            raise HTTPException(404, detail="group not found")
        stmt = select(Expense).where(Expense.group_id == gid)
        rows = s.exec(stmt).all()
        return [ExpenseRead(id=r.id, payer_id=r.payer_id, amount=r.amount,
                            description=r.description, date=r.date, split_type=r.split_type) for r in rows]

@app.post("/groups/{gid}/settlements")
def add_settlement(gid: int, payload: SettlementCreate):
    with Session(ENGINE) as s:
        if not s.get(Group, gid):
            raise HTTPException(404, detail="group not found")
        ensure_members(s, gid, [payload.from_user_id, payload.to_user_id])
        st = Settlement(group_id=gid, **payload.model_dump())
        s.add(st); s.commit(); s.refresh(st)
        return {"id": st.id, **payload.model_dump()}

@app.get("/groups/{gid}/balance", response_model=BalanceRead)
def group_balance(gid: int):
    with Session(ENGINE) as s:
        if not s.get(Group, gid):
            raise HTTPException(404, detail="group not found")
        balances = compute_balances(s, gid)
        # simple suggestions (greedy): match biggest creditor with biggest debtor
        creditors = sorted([(u, v) for u, v in balances.items() if v > 0], key=lambda x: -x[1])
        debtors = sorted([(u, -v) for u, v in balances.items() if v < 0], key=lambda x: -x[1])
        i = j = 0
        suggestions = []
        while i < len(creditors) and j < len(debtors):
            cu, ca = creditors[i];
            du, da = debtors[j]
            pay = round(min(ca, da), 2)
            if pay > 0:
                suggestions.append({"from": du, "to": cu, "amount": pay})
                ca = round(ca - pay, 2); da = round(da - pay, 2)
            if ca == 0:
                i += 1
            else:
                creditors[i] = (cu, ca)
            if da == 0:
                j += 1
            else:
                debtors[j] = (du, da)
        return BalanceRead(balances=balances, suggestions=suggestions)

app.mount("/ui", StaticFiles(directory="static", html=True), name="static")
