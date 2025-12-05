from fastapi import APIRouter, HTTPException, Query, Depends
from app.models import (
    MCQQuestionCreate, TheoryQuestionCreate, CodingQuestionCreate,
    QuestionUpdate, MCQOptionUpdate, TheoryDetailsUpdate, CodingDetailsUpdate,
    APIResponse, QuestionTypeEnum
)
from app.services.question_service import question_service
from app.services.test_service import test_service
from app.auth.dependencies import get_current_user, require_role
from uuid import UUID
from typing import Optional

router = APIRouter(prefix="/questions", tags=["Questions"])


# ============ CREATE MCQ QUESTION ============
@router.post("/mcq", response_model=APIResponse, status_code=201)
def create_mcq_question(
    question_data: MCQQuestionCreate,
    current_user: dict = Depends(require_role("institution"))
):
    """
    📝 Create MCQ Question
    
    - 4 options (A, B, C, D)
    - One correct answer
    - Optional explanation
    """
    # Verify test exists and belongs to user
    test = test_service.get_test_by_id(question_data.test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found!")
    
    if str(test.get("created_by")) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to add questions to this test")
    
    new_question = question_service.create_mcq_question(question_data)
    
    if not new_question:
        raise HTTPException(status_code=500, detail="Failed to create question")
    
    return APIResponse(
        success=True,
        message="MCQ question created!",
        data=new_question
    )


# ============ CREATE THEORY QUESTION ============
@router.post("/theory", response_model=APIResponse, status_code=201)
def create_theory_question(
    question_data: TheoryQuestionCreate,
    current_user: dict = Depends(require_role("institution"))
):
    """
    📝 Create Theory Question
    
    - Long answer type
    - Word limit
    - Sample answer (for evaluation)
    - Keywords (for auto-evaluation)
    """
    test = test_service.get_test_by_id(question_data.test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found!")
    
    if str(test.get("created_by")) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_question = question_service.create_theory_question(question_data)
    
    if not new_question:
        raise HTTPException(status_code=500, detail="Failed to create question")
    
    return APIResponse(
        success=True,
        message="Theory question created!",
        data=new_question
    )


# ============ CREATE CODING QUESTION ============
@router.post("/coding", response_model=APIResponse, status_code=201)
def create_coding_question(
    question_data: CodingQuestionCreate,
    current_user: dict = Depends(require_role("institution"))
):
    """
    💻 Create Coding Question
    
    - Programming language selection
    - Starter code template
    - Test cases (visible + hidden)
    - Time & memory limits
    """
    test = test_service.get_test_by_id(question_data.test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found!")
    
    if str(test.get("created_by")) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_question = question_service.create_coding_question(question_data)
    
    if not new_question:
        raise HTTPException(status_code=500, detail="Failed to create question")
    
    return APIResponse(
        success=True,
        message="Coding question created!",
        data=new_question
    )


# ============ GET QUESTIONS BY TEST ============
@router.get("/test/{test_id}", response_model=APIResponse)
def get_questions_by_test(
    test_id: UUID,
    question_type: Optional[QuestionTypeEnum] = Query(None, description="Filter by type: mcq, theory, coding")
):
    """📋 Get All Questions for a Test"""
    test = test_service.get_test_by_id(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found!")
    
    type_value = question_type.value if question_type else None
    questions = question_service.get_questions_by_test(test_id, type_value)
    
    return APIResponse(
        success=True,
        message=f"Found {len(questions)} questions",
        data=questions
    )


# ============ GET SINGLE QUESTION ============
@router.get("/{question_id}", response_model=APIResponse)
def get_question(question_id: UUID):
    """📖 Get Single Question with Details"""
    question = question_service.get_question_by_id(question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found!")
    
    return APIResponse(
        success=True,
        message="Question found!",
        data=question
    )


# ============ UPDATE QUESTION ============
@router.put("/{question_id}", response_model=APIResponse)
def update_question(
    question_id: UUID,
    update_data: QuestionUpdate,
    current_user: dict = Depends(require_role("institution"))
):
    """✏️ Update Question Base Data"""
    question = question_service.get_question_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found!")
    
    updated = question_service.update_question(question_id, update_data)
    
    return APIResponse(
        success=True,
        message="Question updated!",
        data=updated
    )


# ============ UPDATE MCQ OPTIONS ============
@router.put("/{question_id}/mcq-options", response_model=APIResponse)
def update_mcq_options(
    question_id: UUID,
    update_data: MCQOptionUpdate,
    current_user: dict = Depends(require_role("institution"))
):
    """✏️ Update MCQ Options"""
    question = question_service.get_question_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found!")
    
    if question["question_type"] != "mcq":
        raise HTTPException(status_code=400, detail="Not an MCQ question!")
    
    updated = question_service.update_mcq_options(question_id, update_data)
    
    return APIResponse(
        success=True,
        message="MCQ options updated!",
        data=updated
    )


# ============ UPDATE THEORY DETAILS ============
@router.put("/{question_id}/theory-details", response_model=APIResponse)
def update_theory_details(
    question_id: UUID,
    update_data: TheoryDetailsUpdate,
    current_user: dict = Depends(require_role("institution"))
):
    """✏️ Update Theory Details"""
    question = question_service.get_question_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found!")
    
    if question["question_type"] != "theory":
        raise HTTPException(status_code=400, detail="Not a theory question!")
    
    updated = question_service.update_theory_details(question_id, update_data)
    
    return APIResponse(
        success=True,
        message="Theory details updated!",
        data=updated
    )


# ============ UPDATE CODING DETAILS ============
@router.put("/{question_id}/coding-details", response_model=APIResponse)
def update_coding_details(
    question_id: UUID,
    update_data: CodingDetailsUpdate,
    current_user: dict = Depends(require_role("institution"))
):
    """✏️ Update Coding Details"""
    question = question_service.get_question_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found!")
    
    if question["question_type"] != "coding":
        raise HTTPException(status_code=400, detail="Not a coding question!")
    
    updated = question_service.update_coding_details(question_id, update_data)
    
    return APIResponse(
        success=True,
        message="Coding details updated!",
        data=updated
    )


# ============ DELETE QUESTION ============
@router.delete("/{question_id}", response_model=APIResponse)
def delete_question(
    question_id: UUID,
    current_user: dict = Depends(require_role("institution"))
):
    """🗑️ Delete Question"""
    question = question_service.get_question_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found!")
    
    deleted = question_service.delete_question(question_id)
    
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete")
    
    return APIResponse(
        success=True,
        message="Question deleted!",
        data={"deleted_id": str(question_id)}
    )