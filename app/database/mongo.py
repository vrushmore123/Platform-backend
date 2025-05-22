from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING

try:
    mongodb = AsyncIOMotorClient("mongodb://localhost:27017")
    db = mongodb.liahub_db  # Database name
    
    # Collections
    courses_collection = db.course
    teacher_course_collection = db.teacher_courses  # Fixed variable name
    profile_collection = db.profile
    
    print("MongoDB connection successful!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

async def get_db():
    return db