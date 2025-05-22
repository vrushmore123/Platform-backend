from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.database.mongo import profile_collection
from bson import ObjectId

router = APIRouter()

class CreateProfileModel(BaseModel):
    full_name: str
    email: EmailStr
    bio: Optional[str] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None

class ProfileModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="id")  # alias set to 'id' for clarity
    full_name: str
    email: EmailStr
    bio: Optional[str] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ProfileUpdateModel(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None


def fix_id(profile_dict):
    if profile_dict and "_id" in profile_dict:
        profile_dict["id"] = str(profile_dict["_id"])  # convert ObjectId to str and assign to 'id'
        del profile_dict["_id"]  # delete original MongoDB _id field
    return profile_dict


@router.post("/", response_model=ProfileModel)
async def create_profile(profile: CreateProfileModel):
    profile_dict = profile.dict(exclude_unset=True)
    result = await profile_collection.insert_one(profile_dict)
    new_profile = await profile_collection.find_one({"_id": result.inserted_id})
    if not new_profile:
        raise HTTPException(status_code=404, detail="Failed to retrieve created profile")

    new_profile = fix_id(new_profile)
    return new_profile


@router.get("/{profile_id}", response_model=ProfileModel)
async def get_profile(profile_id: str):
    if not ObjectId.is_valid(profile_id):
        raise HTTPException(status_code=400, detail="Invalid profile ID")
    profile = await profile_collection.find_one({"_id": ObjectId(profile_id)})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile = fix_id(profile)
    return profile


@router.put("/{profile_id}", response_model=ProfileModel)
async def update_profile(profile_id: str, update: ProfileUpdateModel):
    if not ObjectId.is_valid(profile_id):
        raise HTTPException(status_code=400, detail="Invalid profile ID")
    
    update_data = {k: v for k, v in update.dict(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No update fields provided")

    result = await profile_collection.update_one(
        {"_id": ObjectId(profile_id)},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found or not modified")

    updated = await profile_collection.find_one({"_id": ObjectId(profile_id)})
    updated = fix_id(updated)
    return updated
