from fastapi import APIRouter, HTTPException
from app.models.user import UserRegister, UserLogin
from app.models.student import StudentRegister, StudentLogin
from app.database.mongo import db
import bcrypt

router = APIRouter()

# Register User
@router.post("/register/user")
async def register_user(user: UserRegister):
    user_exist = await db.users.find_one({"username": user.username})
    if user_exist:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    await db.users.insert_one(user_dict)
    return {"message": "User registered successfully"}

# Register Student
@router.post("/register/student")
async def register_student(student: StudentRegister):
    student_exist = await db.students.find_one({"email": student.email})
    if student_exist:
        raise HTTPException(status_code=400, detail="Student already exists")
    await db.students.insert_one(student.dict())
    return {"message": "Student registered successfully"}

# Login User
@router.post("/login/user")
async def login_user(user: UserLogin):
    user_db = await db.users.find_one({"username": user.username})
    if not user_db or user.password != user_db["password"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "User login successful"}

# Login Student
@router.post("/login/student")
async def login_student(student: StudentLogin):
    student_db = await db.students.find_one({"email": student.email})
    if not student_db or student.password != student_db["password"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Student login successful"}
