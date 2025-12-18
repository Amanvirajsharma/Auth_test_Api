from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID
from enum import Enum
import re


# ============ ENUMS ============
class RoleEnum(str, Enum):
    USER = "user"
    INSTITUTION = "institution"

class CountryEnum(str, Enum):
    INDIA = "India"

class StateEnum(str, Enum):
    MADHYA_PRADESH = "Madhya Pradesh"

class CityEnum(str, Enum):
    BHOPAL = "Bhopal"
    INDORE = "Indore"

class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"

class QuestionTypeEnum(str, Enum):
    MCQ = "mcq"
    THEORY = "theory"
    CODING = "coding"

class CorrectOptionEnum(str, Enum):
    A = "a"
    B = "b"
    C = "c"
    D = "d"

class ProgrammingLanguageEnum(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    C = "c"

class AttemptStatusEnum(str, Enum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    EVALUATED = "evaluated"


# ============ AUTH MODELS ============
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["Rahul Sharma"])
    email: str = Field(..., examples=["rahul@example.com"])
    password: str = Field(..., min_length=6, max_length=100, examples=["secret123"])
    role: RoleEnum = Field(default=RoleEnum.USER)
    gender: Optional[GenderEnum] = None
    city: Optional[CityEnum] = None
    state: StateEnum = Field(default=StateEnum.MADHYA_PRADESH)
    country: CountryEnum = Field(default=CountryEnum.INDIA)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('Invalid email format')
        return v.lower()

class UserLogin(BaseModel):
    email: str = Field(..., examples=["rahul@example.com"])
    password: str = Field(..., examples=["secret123"])
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return v.lower()

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: str
    gender: Optional[str] = None
    city: Optional[str] = None
    state: str
    country: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class TokenResponse(BaseModel):
    """Login success response with token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class AuthResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class DifficultyEnum(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# ============ PROFILE MODELS ============
class ProfileCreate(BaseModel):
    user_id: UUID                     # 🔑 AUTH user id
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., examples=["rahul@example.com"])
    phone: Optional[str] = None
    bio: Optional[str] = None
    date_of_birth: date = Field(
        ...,
        description="Date of Birth (YYYY-MM-DD)",
        examples=["2000-05-15"]
    )
    avatar_url: Optional[str] = None
    gender: Optional[GenderEnum] = None
    city: Optional[CityEnum] = None
    state: StateEnum = StateEnum.MADHYA_PRADESH
    country: CountryEnum = CountryEnum.INDIA
    role: RoleEnum = RoleEnum.USER

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v):
        return v.lower()


    
 

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=15)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    address: Optional[str] = None
    city: Optional[CityEnum] = None
    state: Optional[StateEnum] = None
    country: Optional[CountryEnum] = None
    is_active: Optional[bool] = None
    role: Optional[RoleEnum] = None

class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str
    phone: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    gender: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



class RoleStats(BaseModel):
    total_users: int
    total_institutions: int
    total_profiles: int


# ============ RESPONSE MODELS ============
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict | list] = None

class PaginatedResponse(BaseModel):
    success: bool
    message: str
    data: list
    total: int
    page: int
    limit: int


# ============ TEST MODELS ============
class TestCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None

    difficulty: DifficultyEnum = DifficultyEnum.MEDIUM   # 🔥 ADD THIS

    duration_minutes: int = Field(default=60, ge=5, le=300)
    total_marks: int = Field(default=100, ge=1)
    passing_marks: int = Field(default=40, ge=0)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class TestUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None

    difficulty: Optional[DifficultyEnum] = None   # 🔥 ADD THIS

    duration_minutes: Optional[int] = Field(None, ge=5, le=300)
    total_marks: Optional[int] = Field(None, ge=1)
    passing_marks: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    is_published: Optional[bool] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class TestResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None

    difficulty: str        # 🔥 ADD THIS

    duration_minutes: int
    total_marks: int
    passing_marks: int
    created_by: Optional[UUID] = None
    is_active: bool
    is_published: bool
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    question_count: Optional[int] = 0


# ============ MCQ MODELS ============
class MCQOptionCreate(BaseModel):
    option_a: str = Field(..., examples=["Python"])
    option_b: str = Field(..., examples=["Java"])
    option_c: str = Field(..., examples=["JavaScript"])
    option_d: str = Field(..., examples=["C++"])
    correct_option: CorrectOptionEnum = Field(..., examples=["a"])
    explanation: Optional[str] = Field(None, examples=["Python is correct because..."])

class MCQQuestionCreate(BaseModel):
    test_id: UUID
    question_text: str = Field(..., min_length=10, examples=["Which language is best for beginners?"])
    marks: int = Field(default=1, ge=1, examples=[1])
    order_no: int = Field(default=1, ge=1)
    options: MCQOptionCreate

class MCQOptionUpdate(BaseModel):
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_option: Optional[CorrectOptionEnum] = None
    explanation: Optional[str] = None


# ============ THEORY MODELS ============
class TheoryDetailsCreate(BaseModel):
    word_limit: int = Field(default=500, ge=50, le=5000, examples=[500])
    sample_answer: Optional[str] = Field(None, examples=["A good answer should cover..."])
    keywords: Optional[List[str]] = Field(None, examples=[["OOP", "inheritance", "polymorphism"]])

class TheoryQuestionCreate(BaseModel):
    test_id: UUID
    question_text: str = Field(..., min_length=10, examples=["Explain OOP concepts in detail."])
    marks: int = Field(default=5, ge=1, examples=[5])
    order_no: int = Field(default=1, ge=1)
    details: TheoryDetailsCreate

class TheoryDetailsUpdate(BaseModel):
    word_limit: Optional[int] = Field(None, ge=50, le=5000)
    sample_answer: Optional[str] = None
    keywords: Optional[List[str]] = None


# ============ CODING MODELS ============
class TestCase(BaseModel):
    input: str = Field(..., examples=["5"])
    expected_output: str = Field(..., examples=["120"])
    is_hidden: bool = Field(default=False)

class CodingDetailsCreate(BaseModel):
    programming_language: ProgrammingLanguageEnum = Field(default=ProgrammingLanguageEnum.PYTHON)
    starter_code: Optional[str] = Field(None, examples=["def factorial(n):\n    pass"])
    solution_code: Optional[str] = Field(None, examples=["def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)"])
    time_limit_seconds: int = Field(default=5, ge=1, le=30, examples=[5])
    memory_limit_mb: int = Field(default=256, ge=32, le=512, examples=[256])
    test_cases: List[TestCase] = Field(default=[])

class CodingQuestionCreate(BaseModel):
    test_id: UUID
    question_text: str = Field(..., min_length=10, examples=["Write a function to calculate factorial."])
    marks: int = Field(default=10, ge=1, examples=[10])
    order_no: int = Field(default=1, ge=1)
    details: CodingDetailsCreate

class CodingDetailsUpdate(BaseModel):
    programming_language: Optional[ProgrammingLanguageEnum] = None
    starter_code: Optional[str] = None
    solution_code: Optional[str] = None
    time_limit_seconds: Optional[int] = Field(None, ge=1, le=30)
    memory_limit_mb: Optional[int] = Field(None, ge=32, le=512)
    test_cases: Optional[List[TestCase]] = None


# ============ QUESTION UPDATE ============
class QuestionUpdate(BaseModel):
    question_text: Optional[str] = Field(None, min_length=10)
    marks: Optional[int] = Field(None, ge=1)
    order_no: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


# ============ ATTEMPT MODELS ============
class StartAttemptRequest(BaseModel):
    test_id: UUID

class SubmitMCQAnswer(BaseModel):
    question_id: UUID
    selected_option: CorrectOptionEnum

class SubmitTheoryAnswer(BaseModel):
    question_id: UUID
    answer_text: str = Field(..., min_length=1)

class SubmitCodingAnswer(BaseModel):
    question_id: UUID
    code_answer: str = Field(..., min_length=1)

class AttemptResponse(BaseModel):
    id: UUID
    test_id: UUID
    user_id: UUID
    started_at: datetime
    submitted_at: Optional[datetime] = None
    score: int
    status: str