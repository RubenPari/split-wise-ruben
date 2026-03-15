from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import User, GroupMember
from app.schemas.schemas import GroupBalanceResponse, BalanceResponse, SimplifiedPayment, UserResponse
from app.auth.utils import get_current_active_user
from app.services.balance_service import calculate_group_balances

router = APIRouter(prefix="/balances", tags=["balances"])


@router.get("/group/{group_id}", response_model=GroupBalanceResponse)
def get_group_balance(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    balances, simplified = calculate_group_balances(db, group_id)
    
    return GroupBalanceResponse(
        group_id=group_id,
        balances=balances,
        simplified_payments=simplified
    )


@router.get("/group/{group_id}/simplify", response_model=List[SimplifiedPayment])
def get_simplified_payments(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    _, simplified = calculate_group_balances(db, group_id)
    return simplified
