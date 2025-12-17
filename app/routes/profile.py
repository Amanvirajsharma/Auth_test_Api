from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from uuid import UUID

from app.models import (
    ProfileCreate,
    ProfileUpdate,
    APIResponse,
    PaginatedResponse,
    RoleEnum,
    CityEnum,
    GenderEnum
)
from app.services.profile_service import profile_service
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/profiles", tags=["Profiles"])


# ======================================================
# CREATE PROFILE (Logged-in user only)
# ======================================================
@router.post("/", response_model=APIResponse, status_code=201)
def create_profile(
    profile: ProfileCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    ✨ Logged-in user ka profile banao
    - Profile sirf user_id se linked hota hai
    - 1 user = 1 profile
    """

    existing = profile_service.get_profile_by_user_id(current_user["id"])
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Profile already exists for this user"
        )

    new_profile = profile_service.create_profile(
        profile_data=profile,
        user_id=current_user["id"]
    )

    if not new_profile:
        raise HTTPException(
            status_code=500,
            detail="Failed to create profile"
        )

    return APIResponse(
        success=True,
        message="Profile created successfully",
        data=new_profile
    )


# ======================================================
# GET MY PROFILE
# ======================================================
@router.get("/me", response_model=APIResponse)
def get_my_profile(
    current_user: dict = Depends(get_current_user)
):
    """
    👤 Apna profile dekho (self)
    """

    profile = profile_service.get_profile_by_user_id(current_user["id"])

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return APIResponse(
        success=True,
        message="My profile fetched successfully",
        data=profile
    )


# ======================================================
# UPDATE MY PROFILE
# ======================================================
@router.put("/me", response_model=APIResponse)
def update_my_profile(
    profile_update: ProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    ✏️ Apna profile update karo
    """

    updated_profile = profile_service.update_profile(
        user_id=current_user["id"],
        update_data=profile_update
    )

    if not updated_profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return APIResponse(
        success=True,
        message="Profile updated successfully",
        data=updated_profile
    )


# ======================================================
# DELETE MY PROFILE (SOFT DELETE)
# ======================================================
@router.delete("/me", response_model=APIResponse)
def delete_my_profile(
    current_user: dict = Depends(get_current_user)
):
    """
    🗑️ Apna profile delete karo (soft delete)
    """

    deleted = profile_service.delete_profile(current_user["id"])

    if not deleted:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete profile"
        )

    return APIResponse(
        success=True,
        message="Profile deleted successfully"
    )


# ======================================================
# GET PROFILE BY USER ID (Admin / Internal)
# ======================================================
@router.get("/user/{user_id}", response_model=APIResponse)
def get_profile_by_user_id(user_id: UUID):
    """
    🔍 user_id se profile fetch karo
    (Admin / Internal use)
    """

    profile = profile_service.get_profile_by_user_id(user_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return APIResponse(
        success=True,
        message="Profile fetched successfully",
        data=profile
    )


# ======================================================
# LIST / FILTER PROFILES
# ======================================================
@router.get("/", response_model=PaginatedResponse)
def get_all_profiles(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    is_active: Optional[bool] = None,
    role: Optional[RoleEnum] = Query(None, description="user / institution"),
    city: Optional[CityEnum] = Query(None, description="Bhopal / Indore"),
    gender: Optional[GenderEnum] = Query(None, description="Male / Female")
):
    """
    📋 Saare profiles dekho (filters ke saath)
    """

    profiles, total = profile_service.get_all_profiles(
        page=page,
        limit=limit,
        is_active=is_active,
        role=role.value if role else None,
        city=city.value if city else None,
        gender=gender.value if gender else None
    )

    return PaginatedResponse(
        success=True,
        message=f"Found {len(profiles)} profiles",
        data=profiles,
        total=total,
        page=page,
        limit=limit
    )


# ======================================================
# USERS & INSTITUTIONS LIST
# ======================================================
@router.get("/users", response_model=PaginatedResponse)
def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    profiles, total = profile_service.get_users(page, limit)

    return PaginatedResponse(
        success=True,
        message=f"Found {len(profiles)} users",
        data=profiles,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/institutions", response_model=PaginatedResponse)
def get_all_institutions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    profiles, total = profile_service.get_institutions(page, limit)

    return PaginatedResponse(
        success=True,
        message=f"Found {len(profiles)} institutions",
        data=profiles,
        total=total,
        page=page,
        limit=limit
    )
