from app.database import db_client
from app.models import TestCreate, TestUpdate
from typing import Optional
from uuid import UUID


class TestService:
    """Test CRUD operations"""
    
    def __init__(self):
        self.client = db_client
        self.table = "tests"
    
    def create_test(self, test_data: TestCreate, created_by: str) -> Optional[dict]:
        """Create new test"""
        data = test_data.model_dump(exclude_none=True)
        data["created_by"] = created_by
        
        # Convert datetime to string
        if 'start_time' in data and data['start_time']:
            data['start_time'] = data['start_time'].isoformat()
        if 'end_time' in data and data['end_time']:
            data['end_time'] = data['end_time'].isoformat()
        
        response = self.client.from_(self.table).insert(data).execute()
        return response.data[0] if response.data else None
    
    def get_test_by_id(self, test_id: UUID) -> Optional[dict]:
        """Get test by ID with question count"""
        response = self.client.from_(self.table)\
            .select("*")\
            .eq("id", str(test_id))\
            .execute()
        
        if response.data:
            test = response.data[0]
            # Get question count
            q_response = self.client.from_("questions")\
                .select("id", count="exact")\
                .eq("test_id", str(test_id))\
                .execute()
            test["question_count"] = q_response.count if q_response.count else 0
            return test
        
        return None
    
    def get_all_tests(
        self,
        page: int = 1,
        limit: int = 10,
        is_published: Optional[bool] = None,
        created_by: Optional[str] = None
    ) -> tuple[list, int]:
        """Get all tests with pagination"""
        offset = (page - 1) * limit
        
        query = self.client.from_(self.table).select("*", count="exact")
        
        if is_published is not None:
            query = query.eq("is_published", is_published)
        
        if created_by:
            query = query.eq("created_by", created_by)
        
        response = query\
            .eq("is_active", True)\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        total = response.count if response.count else len(response.data)
        return response.data, total
    
    def update_test(self, test_id: UUID, update_data: TestUpdate) -> Optional[dict]:
        """Update test"""
        data = update_data.model_dump(exclude_none=True)
        
        if not data:
            return self.get_test_by_id(test_id)
        
        # Convert datetime
        if 'start_time' in data and data['start_time']:
            data['start_time'] = data['start_time'].isoformat()
        if 'end_time' in data and data['end_time']:
            data['end_time'] = data['end_time'].isoformat()
        
        response = self.client.from_(self.table)\
            .update(data)\
            .eq("id", str(test_id))\
            .execute()
        
        return response.data[0] if response.data else None
    
    def delete_test(self, test_id: UUID) -> bool:
        """Delete test (soft delete)"""
        response = self.client.from_(self.table)\
            .update({"is_active": False})\
            .eq("id", str(test_id))\
            .execute()
        
        return len(response.data) > 0
    
    def publish_test(self, test_id: UUID) -> Optional[dict]:
        """Publish a test"""
        response = self.client.from_(self.table)\
            .update({"is_published": True})\
            .eq("id", str(test_id))\
            .execute()
        
        return response.data[0] if response.data else None
    
    def unpublish_test(self, test_id: UUID) -> Optional[dict]:
        """Unpublish a test"""
        response = self.client.from_(self.table)\
            .update({"is_published": False})\
            .eq("id", str(test_id))\
            .execute()
        
        return response.data[0] if response.data else None
    
    def get_test_stats(self, test_id: UUID) -> dict:
        """Get test statistics"""
        # Questions count
        q_response = self.client.from_("questions")\
            .select("id, question_type, marks", count="exact")\
            .eq("test_id", str(test_id))\
            .eq("is_active", True)\
            .execute()
        
        questions = q_response.data if q_response.data else []
        
        mcq_count = sum(1 for q in questions if q["question_type"] == "mcq")
        theory_count = sum(1 for q in questions if q["question_type"] == "theory")
        coding_count = sum(1 for q in questions if q["question_type"] == "coding")
        total_marks = sum(q["marks"] for q in questions)
        
        # Attempts count
        a_response = self.client.from_("test_attempts")\
            .select("id", count="exact")\
            .eq("test_id", str(test_id))\
            .execute()
        
        return {
            "total_questions": len(questions),
            "mcq_count": mcq_count,
            "theory_count": theory_count,
            "coding_count": coding_count,
            "total_marks": total_marks,
            "total_attempts": a_response.count if a_response.count else 0
        }


# Singleton
test_service = TestService()