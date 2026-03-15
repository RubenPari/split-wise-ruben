from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database.database import get_db
from app.models.models import User, Group, GroupMember, Expense, ExpenseShare, SplitType
from app.schemas.schemas import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse,
    PaymentCreate, PaymentResponse, SplitTypeEnum
)
from app.auth.utils import get_current_active_user
from app.services.balance_service import calculate_group_balances
from app.core.config import settings
import os
import aiofiles
import uuid

router = APIRouter(prefix="/expenses", tags=["expenses"])

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf'}


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@router.post("/", response_model=ExpenseResponse)
def create_expense(
    expense_data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == expense_data.group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    split_type_map = {
        SplitTypeEnum.EQUAL: SplitType.EQUAL,
        SplitTypeEnum.PERCENTAGE: SplitType.PERCENTAGE,
        SplitTypeEnum.FIXED: SplitType.FIXED,
    }
    
    expense = Expense(
        group_id=expense_data.group_id,
        title=expense_data.title,
        amount=expense_data.amount,
        date=expense_data.date,
        category_id=expense_data.category_id,
        payer_id=expense_data.payer_id,
        notes=expense_data.notes,
        split_type=split_type_map.get(expense_data.split_type, SplitType.EQUAL)
    )
    db.add(expense)
    db.flush()
    
    total_shares = 0.0
    for share_data in expense_data.shares:
        share = ExpenseShare(
            expense_id=expense.id,
            user_id=share_data.user_id,
            share_amount=share_data.share_amount or 0.0,
            share_percentage=share_data.share_percentage
        )
        db.add(share)
        total_shares += share_data.share_amount or 0.0
    
    if abs(total_shares - expense_data.amount) > 0.01:
        raise HTTPException(status_code=400, detail="Shares don't sum to expense amount")
    
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/group/{group_id}", response_model=List[ExpenseResponse])
def get_group_expenses(
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
    
    expenses = db.query(Expense).filter(
        Expense.group_id == group_id
    ).order_by(Expense.date.desc()).all()
    
    return expenses


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == expense.group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    if expense.payer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the payer can edit this expense")
    
    if expense_data.title:
        expense.title = expense_data.title
    if expense_data.amount:
        expense.amount = expense_data.amount
    if expense_data.date:
        expense.date = expense_data.date
    if expense_data.category_id is not None:
        expense.category_id = expense_data.category_id
    if expense_data.notes is not None:
        expense.notes = expense_data.notes
    
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    if expense.payer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the payer can delete this expense")
    
    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted"}


@router.post("/{expense_id}/receipt", response_model=ExpenseResponse)
async def upload_receipt(
    expense_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    if expense.payer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the payer can upload receipt")
    
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    expense.receipt_url = f"/uploads/{unique_filename}"
    db.commit()
    db.refresh(expense)
    return expense


@router.post("/payments", response_model=PaymentResponse)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == payment_data.group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    payment = Payment(
        group_id=payment_data.group_id,
        from_user_id=current_user.id,
        to_user_id=payment_data.to_user_id,
        amount=payment_data.amount,
        notes=payment_data.notes
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
