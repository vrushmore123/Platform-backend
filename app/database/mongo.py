from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING

try:
    mongodb = AsyncIOMotorClient("mongodb+srv://morevrushali234:o5wvF2Amry4Q7FzY@courses.aw0aojx.mongodb.net/?retryWrites=true&w=majority&appName=Courses")
    db = mongodb.liahub_db  # Database name
    
    # Collections
    courses_collection = db.course
    teacher_course_collection = db.teacher_courses  
    profile_collection = db.profile
    
    print("MongoDB connection successful!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

async def get_db():
    return db