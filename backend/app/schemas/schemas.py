from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SplitTypeEnum(str, Enum):
    EQUAL = "equal"
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: Optional[str] = None
    google_id: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_currency: Optional[str] = None


class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str] = None
    preferred_currency: str = "EUR"
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    icon: Optional[str] = None


class CategoryCreate(CategoryBase):
    group_id: int


class CategoryResponse(CategoryBase):
    id: int
    group_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class GroupMemberResponse(BaseModel):
    user_id: int
    user: UserResponse
    role: str
    joined_at: datetime
    
    class Config:
        from_attributes = True


class GroupResponse(GroupBase):
    id: int
    created_by_id: int
    created_at: datetime
    members: List[GroupMemberResponse] = []
    categories: List[CategoryResponse] = []
    
    class Config:
        from_attributes = True


class ExpenseShareBase(BaseModel):
    user_id: int
    share_amount: float
    share_percentage: Optional[float] = None


class ExpenseShareCreate(BaseModel):
    user_id: int
    share_amount: Optional[float] = None
    share_percentage: Optional[float] = None


class ExpenseBase(BaseModel):
    title: str
    amount: float
    date: datetime
    category_id: Optional[int] = None
    payer_id: int
    notes: Optional[str] = None
    split_type: SplitTypeEnum = SplitTypeEnum.EQUAL
    shares: List[ExpenseShareCreate]


class ExpenseCreate(ExpenseBase):
    group_id: int


class ExpenseUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[datetime] = None
    category_id: Optional[int] = None
    notes: Optional[str] = None


class ExpenseShareResponse(ExpenseShareBase):
    id: int
    expense_id: int
    
    class Config:
        from_attributes = True


class ExpenseResponse(ExpenseBase):
    id: int
    group_id: int
    payer_id: int
    receipt_url: Optional[str] = None
    created_at: datetime
    shares: List[ExpenseShareResponse] = []
    
    class Config:
        from_attributes = True


class PaymentBase(BaseModel):
    group_id: int
    to_user_id: int
    amount: float
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    id: int
    from_user_id: int
    paid_at: datetime
    from_user: UserResponse
    to_user: UserResponse
    
    class Config:
        from_attributes = True


class BalanceResponse(BaseModel):
    user_id: int
    user: UserResponse
    amount: float  # positive = owed to them, negative = they owe


class SimplifiedPayment(BaseModel):
    from_user_id: int
    from_user: UserResponse
    to_user_id: int
    to_user: UserResponse
    amount: float


class GroupBalanceResponse(BaseModel):
    group_id: int
    balances: List[BalanceResponse]
    simplified_payments: List[SimplifiedPayment]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
