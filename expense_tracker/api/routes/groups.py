from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from expense_tracker.api.deps import get_db
from expense_tracker.models.group import Group, GroupMember
from expense_tracker.schemas.group import GroupCreate, GroupRead

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=GroupRead)
def create_group(payload: GroupCreate, s: Session = Depends(get_db)):
    if not payload.name.strip():
        raise HTTPException(400, detail="group name required")
    g = Group(name=payload.name.strip())
    s.add(g)
    s.commit()
    s.refresh(g)

    for u in payload.members:
        s.add(GroupMember(group_id=g.id, user_id=u))
    s.commit()

    members = [m.user_id for m in s.exec(select(GroupMember).where(GroupMember.group_id == g.id)).all()]
    return GroupRead(id=g.id, name=g.name, members=members)


@router.get("/{gid}", response_model=GroupRead)
def get_group(gid: int, s: Session = Depends(get_db)):
    g = s.get(Group, gid)
    if not g:
        raise HTTPException(404, detail="group not found")
    stmt = select(GroupMember).where(GroupMember.group_id == gid)
    members = [m.user_id for m in s.exec(stmt).all()]
    return GroupRead(id=g.id, name=g.name, members=members)