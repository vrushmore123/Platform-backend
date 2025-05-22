from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime

courses_db = []


class CourseBase(BaseModel):
    name: str
    description: str
    imageUrl: Optional[HttpUrl] = None
    category: str = "General"

class CourseCreate(CourseBase):
    pass

class CourseInDB(CourseBase):
    id: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None