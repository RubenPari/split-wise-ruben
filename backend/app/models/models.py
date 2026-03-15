from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class SplitType(enum.Enum):
    EQUAL = "equal"
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    preferred_currency = Column(String(10), default="EUR")
    google_id = Column(String(255), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    group_memberships = relationship("GroupMember", back_populates="user")
    expenses_paid = relationship("Expense", back_populates="payer")
    expense_shares = relationship("ExpenseShare", back_populates="user")
    payments_made = relationship("Payment", back_populates="from_user")
    payments_received = relationship("Payment", back_populates="to_user")


class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="group", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="group", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by_id])


class GroupMember(Base):
    __tablename__ = "group_members"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), default="member")  # admin, member
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="group_memberships")


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    icon = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    group = relationship("Group", back_populates="categories")
    expenses = relationship("Expense", back_populates="category")


class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    payer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receipt_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    split_type = Column(Enum(SplitType), default=SplitType.EQUAL)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    group = relationship("Group", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")
    payer = relationship("User", back_populates="expenses_paid")
    shares = relationship("ExpenseShare", back_populates="expense", cascade="all, delete-orphan")


class ExpenseShare(Base):
    __tablename__ = "expense_shares"
    
    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    share_amount = Column(Float, nullable=False)
    share_percentage = Column(Float, nullable=True)
    
    expense = relationship("Expense", back_populates="shares")
    user = relationship("User", back_populates="expense_shares")


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    paid_at = Column(DateTime(timezone=True), server_default=func.now())
    
    group = relationship("Group")
    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="payments_made")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="payments_received")
