from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Tuple
from app.models.models import User, Group, Expense, ExpenseShare, Payment
from app.schemas.schemas import BalanceResponse, SimplifiedPayment, UserResponse


def calculate_group_balances(db: Session, group_id: int) -> Tuple[List[BalanceResponse], List[SimplifiedPayment]]:
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        return [], []
    
    member_ids = [m.user_id for m in group.members]
    if not member_ids:
        return [], []
    
    balances: Dict[int, float] = {user_id: 0.0 for user_id in member_ids}
    
    expenses = db.query(Expense).filter(Expense.group_id == group_id).all()
    for expense in expenses:
        balances[expense.payer_id] += expense.amount
        for share in expense.shares:
            if share.user_id in balances:
                balances[share.user_id] -= share.share_amount
    
    payments = db.query(Payment).filter(Payment.group_id == group_id).all()
    for payment in payments:
        if payment.from_user_id in balances:
            balances[payment.from_user_id] += payment.amount
        if payment.to_user_id in balances:
            balances[payment.to_user_id] -= payment.amount
    
    balance_responses = []
    for user_id in member_ids:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            balance_responses.append(BalanceResponse(
                user_id=user_id,
                user=UserResponse.model_validate(user),
                amount=round(balances[user_id], 2)
            ))
    
    simplified = simplify_balances(db, balances, member_ids)
    
    return balance_responses, simplified


def simplify_balances(db: Session, balances: Dict[int, float], member_ids: List[int]) -> List[SimplifiedPayment]:
    creditors = []
    debtors = []
    
    for user_id in member_ids:
        amount = round(balances.get(user_id, 0.0), 2)
        if amount > 0.01:
            creditors.append((user_id, amount))
        elif amount < -0.01:
            debtors.append((user_id, -amount))
    
    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1], reverse=True)
    
    simplified = []
    
    i, j = 0, 0
    while i < len(creditors) and j < len(debtors):
        creditor_id, credit_amount = creditors[i]
        debtor_id, debt_amount = debtors[j]
        
        transfer_amount = min(credit_amount, debt_amount)
        
        if transfer_amount > 0.01:
            creditor = db.query(User).filter(User.id == creditor_id).first()
            debtor = db.query(User).filter(User.id == debtor_id).first()
            
            if creditor and debtor:
                simplified.append(SimplifiedPayment(
                    from_user_id=debtor_id,
                    from_user=UserResponse.model_validate(debtor),
                    to_user_id=creditor_id,
                    to_user=UserResponse.model_validate(creditor),
                    amount=round(transfer_amount, 2)
                ))
        
        creditors[i] = (creditor_id, credit_amount - transfer_amount)
        debtors[j] = (debtor_id, debt_amount - transfer_amount)
        
        if creditors[i][1] < 0.01:
            i += 1
        if debtors[j][1] < 0.01:
            j += 1
    
    return simplified
