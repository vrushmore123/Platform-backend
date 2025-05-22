from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId

# Custom validator to support BSON ObjectId in output
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

# Base model used for both input and output
class ProfileModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    full_name: str
    email: EmailStr
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "full_name": "Jane Doe",
                "email": "jane@example.com",
                "bio": "A software developer",
                "avatar_url": "https://example.com/avatar.jpg"
            }
        }

class ProfileUpdateModel(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]
    bio: Optional[str]
    avatar_url: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "full_name": "Jane Smith",
                "bio": "Updated bio",
                "avatar_url": "https://example.com/new-avatar.jpg"
            }
        }
