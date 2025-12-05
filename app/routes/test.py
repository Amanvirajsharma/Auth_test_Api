from fastapi import APIRouter, HTTPException, Query, Depends
from app.models import (
    TestCreate, TestUpdate, APIResponse, PaginatedResponse
)
from app.services.test_service import test_service
from app.auth.dependencies import get_current_user, require_role
from uuid import UUID
from typing import Optional

router = APIRouter(prefix="/tests", tags=["Tests"])


# ============ CREATE TEST ============
@router.post("/", response_model=APIResponse, status_code=201)
def create_test(
    test_data: TestCreate,
    current_user: dict = Depends(require_role("institution"))  # Only institution can create
):
    """
    📝 Create New Test
    
    **Only Institution can create tests**
    """
    new_test = test_service.create_test(test_data, current_user["id"])
    
    if not new_test:
        raise HTTPException(status_code=500, detail="Failed to create test")
    
    return APIResponse(
        success=True,
        message="Test created successfully!",
        data=new_test
    )


# ============ GET ALL TESTS ============
@router.get("/", response_model=PaginatedResponse)
def get_all_tests(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    is_published: Optional[bool] = Query(None, description="Filter by published status")
):
    """📋 Get All Tests"""
    tests, total = test_service.get_all_tests(page, limit, is_published)
    
    return PaginatedResponse(
        success=True,
        message=f"Found {len(tests)} tests",
        data=tests,
        total=total,
        page=page,
        limit=limit
    )


# ============ GET MY TESTS (Institution) ============
@router.get("/my-tests", response_model=PaginatedResponse)
def get_my_tests(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(require_role("institution"))
):
    """📋 Get My Created Tests (Institution only)"""
    tests, total = test_service.get_all_tests(page, limit, created_by=current_user["id"])
    
    return PaginatedResponse(
        success=True,
        message=f"Found {len(tests)} tests",
        data=tests,
        total=total,
        page=page,
        limit=limit
    )


# ============ GET SINGLE TEST ============
@router.get("/{test_id}", response_model=APIResponse)
def get_test(test_id: UUID):
    """📖 Get Single Test with Details"""
    test = test_service.get_test_by_id(test_id)
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found!")
    
    return APIResponse(
        success=True,
        message="Test found!",
        data=test
    )


# ============ GET TEST STATS ============
@router.get("/{test_id}/stats", response_model=APIResponse)
def get_test_stats(test_id: UUID):
    """📊 Get Test Statistics"""
    test = test_service.get_test_by_id(test_id)
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found!")
    
    stats = test_service.get_test_stats(test_id)
    
    return APIResponse(
        success=True,
        message="Test statistics fetched!",
        data=stats
    )


# ============ UPDATE TEST ============
@router.put("/{test_id}", response_model=APIResponse)
def update_test(
    test_id: UUID,
    test_update: TestUpdate,
    current_user: dict = Depends(require_role("institution"))
):
    """✏️ Update Test"""
    existing = test_service.get_test_by_id(test_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Test not found!")
    
    # Check ownership
    if str(existing.get("created_by")) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this test")
    
    updated = test_service.update_test(test_id, test_update)
    
    return APIResponse(
        success=True,
        message="Test updated!",
        data=updated
    )


# ============ PUBLISH TEST ============
@router.post("/{test_id}/publish", response_model=APIResponse)
def publish_test(
    test_id: UUID,
    current_user: dict = Depends(require_role("institution"))
):
    """🚀 Publish Test"""
    existing = test_service.get_test_by_id(test_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Test not found!")
    
    if str(existing.get("created_by")) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    updated = test_service.publish_test(test_id)
    
    return APIResponse(
        success=True,
        message="Test published!",
        data=updated
    )


# ============ UNPUBLISH TEST ============
@router.post("/{test_id}/unpublish", response_model=APIResponse)
def unpublish_test(
    test_id: UUID,
    current_user: dict = Depends(require_role("institution"))
):
    """⏸️ Unpublish Test"""
    existing = test_service.get_test_by_id(test_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Test not found!")
    
    if str(existing.get("created_by")) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    updated = test_service.unpublish_test(test_id)
    
    return APIResponse(
        success=True,
        message="Test unpublished!",
        data=updated
    )


# ============ DELETE TEST ============
@router.delete("/{test_id}", response_model=APIResponse)
def delete_test(
    test_id: UUID,
    current_user: dict = Depends(require_role("institution"))
):
    """🗑️ Delete Test"""
    existing = test_service.get_test_by_id(test_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Test not found!")
    
    if str(existing.get("created_by")) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    deleted = test_service.delete_test(test_id)
    
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete")
    
    return APIResponse(
        success=True,
        message="Test deleted!",
        data={"deleted_id": str(test_id)}
    )