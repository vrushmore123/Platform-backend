from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4
from bson import ObjectId
from typing import List, Optional
import os
import base64
from app.database.mongo import teacher_course_collection
from PIL import Image
from io import BytesIO

router = APIRouter()

# ------------------ Models ------------------ #

class Question(BaseModel):
    question: str
    options: List[str]
    correct_answer: int

class Quiz(BaseModel):
    title: str
    questions: List[Question]

class Lesson(BaseModel):
    title: str
    video_url: str
    duration: str
    resource_url: str
    summary: str

class Module(BaseModel):
    title: str
    description: str
    lessons: List[Lesson] = []
    quiz: Optional[Quiz] = None
    id: str = Field(default_factory=lambda: str(ObjectId()))

class CourseBase(BaseModel):
    title: str
    description: str
    category: str = "General"
    level: str = "Beginner"
    status: str = "draft"  
    modules: List[Module] = []

class CourseCreate(CourseBase):
    thumbnail_image: Optional[str] = None

class CourseInDB(CourseBase):
    id: str
    thumbnail_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    student_count: int

    class Config:
        json_encoders = {ObjectId: str}



UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_thumbnail(thumbnail_image: str) -> str:
    if not thumbnail_image.startswith("data:image/"):
        raise HTTPException(status_code=400, detail="Invalid image format")

    try:
        header, encoded = thumbnail_image.split(",", 1)
        file_ext = header.split("/")[1].split(";")[0]
        image_data = base64.b64decode(encoded)
        image = Image.open(BytesIO(image_data))
        image.load()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image: {str(e)}")

    file_id = str(ObjectId())
    filename = f"{file_id}.{file_ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    image.save(filepath)
    return f"/uploads/{filename}"

# ------------------ Routes ------------------ #

@router.post("/", response_model=CourseInDB)
async def create_teacher_course(course: CourseCreate):
    thumbnail_url = save_thumbnail(course.thumbnail_image) if course.thumbnail_image else None

    course_data = {
        "title": course.title,
        "description": course.description,
        "category": course.category,
        "level": course.level,
        "status": course.status or "draft",
        "thumbnail_image": thumbnail_url,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "student_count": 0,
        "modules": []
    }

    for module in course.modules:
        module_data = module.dict(exclude={"id"})
        module_data["id"] = str(ObjectId())
        course_data["modules"].append(module_data)

    result = await teacher_course_collection.insert_one(course_data)
    return CourseInDB(id=str(result.inserted_id), **course_data)

@router.get("/", response_model=List[CourseInDB])
async def get_teacher_courses():
    courses = await teacher_course_collection.find().to_list(100)
    return [parse_course(course) for course in courses]

@router.get("/{course_id}", response_model=CourseInDB)
async def get_teacher_course(course_id: str):
    course = await teacher_course_collection.find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Teacher Course not found")
    return parse_course(course)

@router.put("/{course_id}", response_model=CourseInDB)
async def update_teacher_course(course_id: str, course: CourseCreate):
    thumbnail_url = save_thumbnail(course.thumbnail_image) if course.thumbnail_image else None

    update_data = {
        "title": course.title,
        "description": course.description,
        "category": course.category,
        "level": course.level,
        "status": course.status or "draft",
        "updated_at": datetime.utcnow()
    }

    if thumbnail_url:
        update_data["thumbnail_image"] = thumbnail_url

    if course.modules:
        processed_modules = []
        for module in course.modules:
            module_data = module.dict(exclude={"id"})
            module_data["id"] = str(ObjectId())
            processed_modules.append(module_data)
        update_data["modules"] = processed_modules

    result = await teacher_course_collection.update_one(
        {"_id": ObjectId(course_id)},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Teacher Course not found")

    updated_course = await teacher_course_collection.find_one({"_id": ObjectId(course_id)})
    return parse_course(updated_course)

@router.get("/{course_id}/modules", response_model=List[Module])
async def get_course_modules(course_id: str):
    course = await teacher_course_collection.find_one({"_id": ObjectId(course_id)}, {"modules": 1})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course.get("modules", [])

@router.get("/{course_id}/modules", response_model=List[Module])
async def get_course_modules(course_id: str):
    course = await teacher_course_collection.find_one({"_id": ObjectId(course_id)}, {"modules": 1})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course.get("modules", [])

@router.delete("/{course_id}", response_model=dict)
async def delete_teacher_course(course_id: str):
    result = await teacher_course_collection.delete_one({"_id": ObjectId(course_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Teacher Course not found")
    return {"message": "Teacher Course deleted successfully"}

# ------------------ Utility ------------------ #

def parse_course(course_dict) -> CourseInDB:
    return CourseInDB(
        id=str(course_dict["_id"]),
        title=course_dict["title"],
        description=course_dict["description"],
        category=course_dict.get("category", "General"),
        level=course_dict.get("level", "Beginner"),
        status=course_dict.get("status", "draft"),
        thumbnail_image=course_dict.get("thumbnail_image"),
        created_at=course_dict["created_at"],
        updated_at=course_dict["updated_at"],
        student_count=course_dict.get("student_count", 0),
        modules=course_dict.get("modules", [])
    )
