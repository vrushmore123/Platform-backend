from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl, validator, conbytes
from bson import ObjectId
import re

# Improved ObjectId handling with validation
class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

# Constants
MAX_PDF_SIZE = 5_000_000  # 5MB
DURATION_PATTERN = r"^([0-5]?\d):([0-5]?\d)$"

# -- Lesson Model --
class Lesson(BaseModel):
    """Represents a single lesson within a module"""
    title: str = Field(..., min_length=1, max_length=100, example="Introduction to Python")
    video_url: Optional[HttpUrl] = Field(
        None,
        example="https://example.com/video1.mp4",
        description="URL to lesson video content"
    )
    duration: Optional[str] = Field(
        None,
        regex=DURATION_PATTERN,
        example="15:30",
        description="Duration in MM:SS format"
    )
    resource_url: Optional[HttpUrl] = Field(
        None,
        example="https://example.com/resources.zip",
        description="URL to downloadable resources"
    )
    summary: Optional[str] = Field(
        None,
        max_length=500,
        example="This lesson covers basic Python syntax and concepts"
    )

    @validator('*', pre=True)
    def strip_whitespace(cls, v, field):
        if isinstance(v, str):
            return v.strip()
        return v

# -- Quiz Models --
class QuizQuestion(BaseModel):
    """Represents a single question in a quiz"""
    question: str = Field(..., min_length=10, max_length=500, example="What is 2+2?")
    options: List[str] = Field(
        ...,
        min_items=4,
        max_items=4,
        example=["3", "4", "5", "6"],
        description="Exactly 4 answer options"
    )
    correct_answer: int = Field(
        ...,
        ge=0,
        le=3,
        example=1,
        description="Index of correct answer (0-3)"
    )

class Quiz(BaseModel):
    """Represents a module quiz"""
    title: str = Field(
        "Module Quiz",
        min_length=1,
        max_length=100,
        example="Python Basics Quiz"
    )
    questions: List[QuizQuestion] = Field(
        ...,
        min_items=1,
        description="At least one question required"
    )

# -- Module Model --
class Module(BaseModel):
    """Represents a course module containing lessons and optional quiz"""
    title: str = Field(..., min_length=1, max_length=100, example="Python Fundamentals")
    description: Optional[str] = Field(
        None,
        max_length=500,
        example="Learn basic Python programming concepts"
    )
    lessons: List[Lesson] = Field(
        ...,
        min_items=1,
        description="At least one lesson required"
    )
    quiz: Optional[Quiz] = Field(
        None,
        description="Optional end-of-module quiz"
    )

# -- Base Course Model --
class CourseBase(BaseModel):
    """Base course model with common fields"""
    title: str = Field(
        ...,
        min_length=5,
        max_length=100,
        example="Complete Python Bootcamp",
        description="Public course title"
    )
    description: str = Field(
        ...,
        min_length=50,
        max_length=2000,
        example="Master Python programming from scratch to advanced level",
        description="Detailed course description"
    )
    category: Literal["web", "mobile", "data", "design"] = Field(
        ...,
        example="web",
        description="Course category from predefined options"
    )

# -- Course Creation Model --
class CourseCreate(CourseBase):
    """Model for creating new courses"""
    thumbnail_pdf: Optional[conbytes(max_length=MAX_PDF_SIZE)] = Field(
        None,
        description="PDF brochure content (max 5MB)"
    )
    modules: List[Module] = Field(
        ...,
        min_items=1,
        example=[{
            "title": "Introduction",
            "lessons": [{
                "title": "Welcome",
                "duration": "05:00"
            }]
        }],
        description="Course curriculum structure"
    )

class Course(CourseBase):
    """Full course model with system-generated fields"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    thumbnail_url: Optional[HttpUrl] = Field(
        None,
        example="https://example.com/course-brochure.pdf",
        description="URL to course brochure PDF"
    )
    created_at: datetime = Field(..., example="2023-08-01T12:00:00Z")
    updated_at: datetime = Field(..., example="2023-08-01T12:00:00Z")
    student_count: int = Field(
        0,
        ge=0,
        example=150,
        description="Number of enrolled students"
    )
    modules: List[Module]

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "_id": "64c3b58e5a0f5f3d8c8b4567",
                "title": "Complete Python Bootcamp",
                "description": "Master Python programming...",
                "category": "web",
                "thumbnail_url": "https://example.com/brochure.pdf",
                "created_at": "2023-08-01T12:00:00Z",
                "updated_at": "2023-08-01T12:00:00Z",
                "student_count": 150,
                "modules": []
            }
        }