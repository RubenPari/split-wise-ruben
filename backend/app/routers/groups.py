from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.models import User, Group, GroupMember, Category
from app.schemas.schemas import (
    GroupCreate, GroupUpdate, GroupResponse, GroupMemberResponse,
    CategoryCreate, CategoryResponse, UserResponse
)
from app.auth.utils import get_current_active_user
import os
import aiofiles

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=GroupResponse)
def create_group(
    group_data: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    new_group = Group(
        name=group_data.name,
        description=group_data.description,
        created_by_id=current_user.id
    )
    db.add(new_group)
    db.flush()
    
    member = GroupMember(
        group_id=new_group.id,
        user_id=current_user.id,
        role="admin"
    )
    db.add(member)
    
    default_categories = [
        Category(group_id=new_group.id, name="Cibo", icon="restaurant"),
        Category(group_id=new_group.id, name="Trasporti", icon="car"),
        Category(group_id=new_group.id, name="Alloggio", icon="home"),
        Category(group_id=new_group.id, name="Divertimento", icon="party"),
        Category(group_id=new_group.id, name="Altro", icon="ellipsis-horizontal"),
    ]
    for cat in default_categories:
        db.add(cat)
    
    db.commit()
    db.refresh(new_group)
    return new_group


@router.get("/", response_model=List[GroupResponse])
def get_my_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    memberships = db.query(GroupMember).filter(GroupMember.user_id == current_user.id).all()
    group_ids = [m.group_id for m in memberships]
    groups = db.query(Group).filter(Group.id.in_(group_ids)).all()
    return groups


@router.get("/{group_id}", response_model=GroupResponse)
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    return group


@router.put("/{group_id}", response_model=GroupResponse)
def update_group(
    group_id: int,
    group_data: GroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id,
        GroupMember.role == "admin"
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Only admins can update the group")
    
    if group_data.name:
        group.name = group_data.name
    if group_data.description is not None:
        group.description = group_data.description
    
    db.commit()
    db.refresh(group)
    return group


@router.delete("/{group_id}")
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    if group.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the creator can delete the group")
    
    db.delete(group)
    db.commit()
    return {"message": "Group deleted"}


@router.post("/{group_id}/members", response_model=GroupMemberResponse)
def add_member(
    group_id: int,
    email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    new_user = db.query(User).filter(User.email == email).first()
    if not new_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == new_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already in group")
    
    new_member = GroupMember(
        group_id=group_id,
        user_id=new_user.id,
        role="member"
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member


@router.delete("/{group_id}/members/{user_id}")
def remove_member(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id,
        GroupMember.role == "admin"
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Only admins can remove members")
    
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    db.delete(member)
    db.commit()
    return {"message": "Member removed"}


@router.post("/{group_id}/categories", response_model=CategoryResponse)
def create_category(
    group_id: int,
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    category = Category(
        group_id=group_id,
        name=category_data.name,
        icon=category_data.icon
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
