from app.database import db_client
from app.models import (
    MCQQuestionCreate, TheoryQuestionCreate, CodingQuestionCreate,
    QuestionUpdate, MCQOptionUpdate, TheoryDetailsUpdate, CodingDetailsUpdate
)
from typing import Optional, List
from uuid import UUID
import json


class QuestionService:
    """Question CRUD operations"""
    
    def __init__(self):
        self.client = db_client
    
    # ============ MCQ QUESTIONS ============
    def create_mcq_question(self, question_data: MCQQuestionCreate) -> Optional[dict]:
        """Create MCQ question with options"""
        # Insert question
        q_data = {
            "test_id": str(question_data.test_id),
            "question_type": "mcq",
            "question_text": question_data.question_text,
            "marks": question_data.marks,
            "order_no": question_data.order_no
        }
        
        q_response = self.client.from_("questions").insert(q_data).execute()
        
        if not q_response.data:
            return None
        
        question = q_response.data[0]
        
        # Insert options
        opt_data = {
            "question_id": question["id"],
            "option_a": question_data.options.option_a,
            "option_b": question_data.options.option_b,
            "option_c": question_data.options.option_c,
            "option_d": question_data.options.option_d,
            "correct_option": question_data.options.correct_option.value,
            "explanation": question_data.options.explanation
        }
        
        opt_response = self.client.from_("mcq_options").insert(opt_data).execute()
        
        if opt_response.data:
            question["options"] = opt_response.data[0]
        
        return question
    
    # ============ THEORY QUESTIONS ============
    def create_theory_question(self, question_data: TheoryQuestionCreate) -> Optional[dict]:
        """Create Theory question"""
        # Insert question
        q_data = {
            "test_id": str(question_data.test_id),
            "question_type": "theory",
            "question_text": question_data.question_text,
            "marks": question_data.marks,
            "order_no": question_data.order_no
        }
        
        q_response = self.client.from_("questions").insert(q_data).execute()
        
        if not q_response.data:
            return None
        
        question = q_response.data[0]
        
        # Insert details
        detail_data = {
            "question_id": question["id"],
            "word_limit": question_data.details.word_limit,
            "sample_answer": question_data.details.sample_answer,
            "keywords": question_data.details.keywords
        }
        
        detail_response = self.client.from_("theory_details").insert(detail_data).execute()
        
        if detail_response.data:
            question["details"] = detail_response.data[0]
        
        return question
    
    # ============ CODING QUESTIONS ============
    def create_coding_question(self, question_data: CodingQuestionCreate) -> Optional[dict]:
        """Create Coding question"""
        # Insert question
        q_data = {
            "test_id": str(question_data.test_id),
            "question_type": "coding",
            "question_text": question_data.question_text,
            "marks": question_data.marks,
            "order_no": question_data.order_no
        }
        
        q_response = self.client.from_("questions").insert(q_data).execute()
        
        if not q_response.data:
            return None
        
        question = q_response.data[0]
        
        # Convert test cases to JSON
        test_cases = [tc.model_dump() for tc in question_data.details.test_cases]
        
        # Insert details
        detail_data = {
            "question_id": question["id"],
            "programming_language": question_data.details.programming_language.value,
            "starter_code": question_data.details.starter_code,
            "solution_code": question_data.details.solution_code,
            "time_limit_seconds": question_data.details.time_limit_seconds,
            "memory_limit_mb": question_data.details.memory_limit_mb,
            "test_cases": json.dumps(test_cases)
        }
        
        detail_response = self.client.from_("coding_details").insert(detail_data).execute()
        
        if detail_response.data:
            question["details"] = detail_response.data[0]
        
        return question
    
    # ============ GET QUESTIONS ============
    def get_question_by_id(self, question_id: UUID) -> Optional[dict]:
        """Get question with details"""
        q_response = self.client.from_("questions")\
            .select("*")\
            .eq("id", str(question_id))\
            .execute()
        
        if not q_response.data:
            return None
        
        question = q_response.data[0]
        
        # Get type-specific details
        if question["question_type"] == "mcq":
            opt_response = self.client.from_("mcq_options")\
                .select("*")\
                .eq("question_id", str(question_id))\
                .execute()
            if opt_response.data:
                question["options"] = opt_response.data[0]
        
        elif question["question_type"] == "theory":
            detail_response = self.client.from_("theory_details")\
                .select("*")\
                .eq("question_id", str(question_id))\
                .execute()
            if detail_response.data:
                question["details"] = detail_response.data[0]
        
        elif question["question_type"] == "coding":
            detail_response = self.client.from_("coding_details")\
                .select("*")\
                .eq("question_id", str(question_id))\
                .execute()
            if detail_response.data:
                question["details"] = detail_response.data[0]
        
        return question
    
    def get_questions_by_test(
        self, 
        test_id: UUID, 
        question_type: Optional[str] = None
    ) -> List[dict]:
        """Get all questions for a test"""
        query = self.client.from_("questions")\
            .select("*")\
            .eq("test_id", str(test_id))\
            .eq("is_active", True)
        
        if question_type:
            query = query.eq("question_type", question_type)
        
        response = query.order("order_no").execute()
        
        questions = response.data if response.data else []
        
        # Get details for each question
        for q in questions:
            if q["question_type"] == "mcq":
                opt = self.client.from_("mcq_options")\
                    .select("*")\
                    .eq("question_id", q["id"])\
                    .execute()
                if opt.data:
                    q["options"] = opt.data[0]
            
            elif q["question_type"] == "theory":
                det = self.client.from_("theory_details")\
                    .select("*")\
                    .eq("question_id", q["id"])\
                    .execute()
                if det.data:
                    q["details"] = det.data[0]
            
            elif q["question_type"] == "coding":
                det = self.client.from_("coding_details")\
                    .select("*")\
                    .eq("question_id", q["id"])\
                    .execute()
                if det.data:
                    q["details"] = det.data[0]
        
        return questions
    
    # ============ UPDATE QUESTIONS ============
    def update_question(self, question_id: UUID, update_data: QuestionUpdate) -> Optional[dict]:
        """Update question base data"""
        data = update_data.model_dump(exclude_none=True)
        
        if not data:
            return self.get_question_by_id(question_id)
        
        response = self.client.from_("questions")\
            .update(data)\
            .eq("id", str(question_id))\
            .execute()
        
        return self.get_question_by_id(question_id) if response.data else None
    
    def update_mcq_options(self, question_id: UUID, update_data: MCQOptionUpdate) -> Optional[dict]:
        """Update MCQ options"""
        data = update_data.model_dump(exclude_none=True)
        
        if 'correct_option' in data:
            data['correct_option'] = data['correct_option'].value if hasattr(data['correct_option'], 'value') else data['correct_option']
        
        if data:
            self.client.from_("mcq_options")\
                .update(data)\
                .eq("question_id", str(question_id))\
                .execute()
        
        return self.get_question_by_id(question_id)
    
    def update_theory_details(self, question_id: UUID, update_data: TheoryDetailsUpdate) -> Optional[dict]:
        """Update theory details"""
        data = update_data.model_dump(exclude_none=True)
        
        if data:
            self.client.from_("theory_details")\
                .update(data)\
                .eq("question_id", str(question_id))\
                .execute()
        
        return self.get_question_by_id(question_id)
    
    def update_coding_details(self, question_id: UUID, update_data: CodingDetailsUpdate) -> Optional[dict]:
        """Update coding details"""
        data = update_data.model_dump(exclude_none=True)
        
        if 'programming_language' in data:
            data['programming_language'] = data['programming_language'].value if hasattr(data['programming_language'], 'value') else data['programming_language']
        
        if 'test_cases' in data:
            data['test_cases'] = json.dumps([tc.model_dump() if hasattr(tc, 'model_dump') else tc for tc in data['test_cases']])
        
        if data:
            self.client.from_("coding_details")\
                .update(data)\
                .eq("question_id", str(question_id))\
                .execute()
        
        return self.get_question_by_id(question_id)
    
    # ============ DELETE QUESTION ============
    def delete_question(self, question_id: UUID) -> bool:
        """Delete question (soft delete)"""
        response = self.client.from_("questions")\
            .update({"is_active": False})\
            .eq("id", str(question_id))\
            .execute()
        
        return len(response.data) > 0


# Singleton
question_service = QuestionService()