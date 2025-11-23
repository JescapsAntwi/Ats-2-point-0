"""
Data models for the ATS Scanner application
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# User Models
class UserCreate(BaseModel):
    """Model for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    name: Optional[str] = None


class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Model for updating user profile"""
    name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)


class UserResponse(BaseModel):
    """Model for user response (without password)"""
    id: str
    email: str
    name: Optional[str] = None
    is_verified: bool = False
    created_at: datetime

    class Config:
        json_encoders = {ObjectId: str}


class VerifyEmail(BaseModel):
    """Model for email verification"""
    email: EmailStr
    verification_code: str = Field(..., min_length=6, max_length=6)


class ResendVerification(BaseModel):
    """Model for resending verification code"""
    email: EmailStr


# Scan Models
class ScanCreate(BaseModel):
    """Model for creating a new scan"""
    resume_text: str
    job_description: str
    resume_filename: Optional[str] = None


class ScanUpdate(BaseModel):
    """Model for updating a scan"""
    resume_text: Optional[str] = None
    job_description: Optional[str] = None
    resume_filename: Optional[str] = None


class ScanResult(BaseModel):
    """Model for scan analysis results"""
    jd_match: int = Field(..., ge=0, le=100, description="JD Match percentage")
    missing_keywords: List[str]
    matched_keywords: List[str]
    profile_summary: str


class ScanResponse(BaseModel):
    """Model for scan response"""
    id: str
    user_id: str
    resume_text: str
    job_description: str
    resume_filename: Optional[str] = None
    ats_score: int
    missing_keywords: List[str]
    matched_keywords: List[str]
    ai_feedback: str
    detailed_improvements: Optional[List[Dict[str, Any]]] = []
    quick_wins: Optional[List[str]] = []
    strengths: Optional[List[str]] = []
    timestamp: datetime

    class Config:
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


class ScanSummary(BaseModel):
    """Lightweight model for scan list (without large text fields)"""
    id: str
    user_id: str
    resume_filename: Optional[str] = None
    ats_score: int
    missing_keywords: List[str]
    matched_keywords: List[str]
    timestamp: datetime

    class Config:
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


class ScanListResponse(BaseModel):
    """Model for list of scans"""
    scans: List[ScanSummary]
    total: int


# Token Models
class Token(BaseModel):
    """Model for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

