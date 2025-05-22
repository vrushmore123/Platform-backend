from pydantic import BaseModel

class StudentRegister(BaseModel):
    name: str
    email: str
    password: str
    course: str

class StudentLogin(BaseModel):
    email: str
    password: str
