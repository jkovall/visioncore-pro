"""User models and schemas"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom type for MongoDB ObjectId with Pydantic v2/v1 compatibility"""
    # Pydantic v2 path
    try:
        from pydantic import core_schema  # type: ignore

        @classmethod
        def __get_pydantic_core_schema__(cls, source, handler):
            def _validate(v, info):
                if not ObjectId.is_valid(v):
                    raise ValueError("Invalid ObjectId")
                return ObjectId(v)

            return cls.core_schema.plain_validator_function(_validate)

        @classmethod
        def __get_pydantic_json_schema__(cls, core_schema, handler):
            return {"type": "string", "pattern": "^[a-f0-9]{24}$"}
    except Exception:
        # Fallback to Pydantic v1 validators
        @classmethod
        def __get_validators__(cls):
            yield cls.validate

        @classmethod
        def validate(cls, v):
            if not ObjectId.is_valid(v):
                raise ValueError("Invalid ObjectId")
            return ObjectId(v)


class UserRegister(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="Password")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "secure_password123",
                "full_name": "John Doe"
            }
        }


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="Password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "secure_password123"
            }
        }


class UserResponse(BaseModel):
    """User response model (no password) - ObjectId represented as string"""
    id: Optional[str] = None
    username: str
    email: EmailStr
    full_name: Optional[str]
    created_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True
        populate_by_name = True


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token data payload"""
    email: str
    exp: Optional[datetime] = None


class UserInDB(BaseModel):
    """User model in database"""
    id: Optional[str] = None
    username: str
    email: EmailStr
    hashed_password: str
    full_name: Optional[str]
    created_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
