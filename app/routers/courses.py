# courses.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
from uuid import uuid4
from app.database.mongo import courses_collection
from app.models.course import CourseInDB,CourseCreate,CourseBase
from bson import ObjectId


router = APIRouter()

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

@router.get("/courses", response_model=List[CourseInDB])
async def get_courses():
    courses = await courses_collection.find().to_list(100)
    return [
        CourseInDB(
            id=str(course["_id"]),
            name=course["name"],
            description=course["description"],
            imageUrl=course.get("imageUrl"),
            category=course.get("category", "General"),
            createdAt=course["createdAt"],
            updatedAt=course.get("updatedAt"),
        )
        for course in courses
    ]

@router.get("/courses/{course_id}", response_model=CourseInDB)
async def get_course(course_id: str):
    course = await courses_collection.find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return CourseInDB(
        id=str(course["_id"]),
        name=course["name"],
        description=course["description"],
        imageUrl=course.get("imageUrl"),
        category=course.get("category", "General"),
        createdAt=course["createdAt"],
        updatedAt=course.get("updatedAt"),
    )

@router.post("/courses", response_model=CourseInDB)
async def create_course(course: CourseCreate):
    new_course = {
        "name": course.name,
        "description": course.description,
        "imageUrl": str(course.imageUrl) if course.imageUrl else f"https://via.placeholder.com/400x200/3b82f6/FFFFFF?text={course.name.replace(' ', '+')}",

        "category": course.category,
        "createdAt": datetime.utcnow(),
        "updatedAt": None
    }
    result = await courses_collection.insert_one(new_course)
    return CourseInDB(id=str(result.inserted_id), **new_course)
