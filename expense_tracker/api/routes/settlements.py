from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from expense_tracker.api.deps import get_db
from expense_tracker.core.logger import logger
from expense_tracker.models.group import Group, GroupMember
from expense_tracker.models.expense import Settlement
from expense_tracker.schemas.expense import SettlementCreate

router = APIRouter(prefix="/groups/{gid}/settlements", tags=["settlements"])


@router.post("")
def add_settlement(gid: int, payload: SettlementCreate, s: Session = Depends(get_db)):
    if not s.get(Group, gid):
        logger.warning("group_not_found_for_settlement", group_id=gid)
        raise HTTPException(404, detail="group not found")

    member_ids = [m.user_id for m in s.exec(select(GroupMember).where(GroupMember.group_id == gid))]
    missing = [u for u in (payload.from_user_id, payload.to_user_id) if u not in member_ids]
    if missing:
        logger.warning("settlement_users_not_in_group", group_id=gid, missing=missing)
        raise HTTPException(400, detail=f"Users not in group: {missing}")

    st = Settlement(group_id=gid, **payload.model_dump())
    s.add(st)
    s.commit()
    s.refresh(st)

    logger.info(
        "settlement_recorded",
        group_id=gid,
        settlement_id=st.id,
        from_user=st.from_user_id,
        to_user=st.to_user_id,
        amount=st.amount,
    )
    return {"id": st.id, **payload.model_dump()}
