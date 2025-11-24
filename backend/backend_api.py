# backend/backend_api.py

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from typing import List, Optional
from bson import ObjectId

# Import models and utilities
from backend.helper import configure_genai, extract_pdf_text, prepare_prompt, get_gemini_response
from backend.database import get_users_collection, get_scans_collection
from backend.models import (
    UserCreate, UserLogin, UserUpdate, UserResponse,
    ScanCreate, ScanUpdate, ScanResponse, ScanSummary, ScanListResponse, Token,
    VerifyEmail, ResendVerification
)
from backend.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from backend.email_service import (
    generate_verification_code, send_verification_email, send_welcome_email
)
from datetime import timedelta

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError(
        "GOOGLE_API_KEY not found in environment variables. "
        "Please create a .env file with your Google API key."
    )

print("✅ Google API key loaded successfully")
configure_genai(api_key)

app = FastAPI(title="ATS Scanner API", version="1.0.0")

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",  # Local development
        "https://*.vercel.app",  # Vercel deployments
        "https://ats-2-point-0.vercel.app",  # Your production frontend (update with your actual URL)
        "*"  # Allow all for now - restrict in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Test MongoDB connection on startup"""
    try:
        from backend.database import get_database
        db = get_database()
        print("✅ MongoDB connection successful!")
        print(f"✅ Database '{db.name}' is ready")
    except Exception as e:
        print(f"⚠️  MongoDB connection warning: {str(e)}")
        print("⚠️  The server will start, but database operations may fail.")
        print("⚠️  Please check your .env file and MongoDB Atlas settings.")


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/signup", response_model=dict, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    """User registration endpoint - creates unverified account and sends verification email"""
    try:
        users_collection = get_users_collection()
        
        # Check if user already exists
        existing_user = users_collection.find_one({"email": user_data.email})
        if existing_user:
            # If user exists but not verified, allow resending verification
            if not existing_user.get("is_verified", False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered but not verified. Please check your email or request a new code."
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Generate verification code
        verification_code = generate_verification_code()
        code_expires_at = datetime.utcnow() + timedelta(minutes=15)
        
        # Hash password and create user
        hashed_password = get_password_hash(user_data.password)
        user_doc = {
            "email": user_data.email,
            "password": hashed_password,
            "is_verified": False,
            "verification_code": verification_code,
            "code_expires_at": code_expires_at,
            "created_at": datetime.utcnow()
        }
        
        # Only add name if it's provided
        if user_data.name:
            user_doc["name"] = user_data.name
        
        result = users_collection.insert_one(user_doc)
        user_id = str(result.inserted_id)
        
        # Send verification email
        try:
            send_verification_email(user_data.email, verification_code, user_data.name)
        except Exception as email_error:
            # If email fails, delete the user and raise error
            users_collection.delete_one({"_id": result.inserted_id})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send verification email: {str(email_error)}"
            )
        
        return {
            "message": "Account created successfully. Please check your email for verification code.",
            "email": user_data.email,
            "user_id": user_id
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in signup endpoint: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/api/auth/verify-email", response_model=Token)
async def verify_email(verification_data: VerifyEmail):
    """Verify email with code and activate account"""
    users_collection = get_users_collection()
    
    # Find user by email
    user = users_collection.find_one({"email": verification_data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already verified
    if user.get("is_verified", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Check if code matches
    if user.get("verification_code") != verification_data.verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Check if code expired
    if user.get("code_expires_at") and user["code_expires_at"] < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code expired. Please request a new one."
        )
    
    # Mark user as verified and remove verification code
    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"is_verified": True},
            "$unset": {"verification_code": "", "code_expires_at": ""}
        }
    )
    
    # Send welcome email
    try:
        send_welcome_email(user["email"], user.get("name"))
    except Exception as e:
        print(f"Failed to send welcome email: {str(e)}")
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "email": user["email"]},
        expires_delta=access_token_expires
    )
    
    # Return user info and token
    user_response = UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        name=user.get("name"),
        is_verified=True,
        created_at=user["created_at"]
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_response)


@app.post("/api/auth/resend-verification", response_model=dict)
async def resend_verification(resend_data: ResendVerification):
    """Resend verification code"""
    users_collection = get_users_collection()
    
    # Find user by email
    user = users_collection.find_one({"email": resend_data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already verified
    if user.get("is_verified", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Generate new verification code
    verification_code = generate_verification_code()
    code_expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    # Update user with new code
    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "verification_code": verification_code,
                "code_expires_at": code_expires_at
            }
        }
    )
    
    # Send verification email
    try:
        send_verification_email(user["email"], verification_code, user.get("name"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification email: {str(e)}"
        )
    
    return {
        "message": "Verification code sent successfully. Please check your email.",
        "email": user["email"]
    }


@app.post("/api/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """User login endpoint"""
    users_collection = get_users_collection()
    
    # Find user by email
    user = users_collection.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if email is verified
    if not user.get("is_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email for verification code."
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "email": user["email"]},
        expires_delta=access_token_expires
    )
    
    # Return user info and token
    user_response = UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        name=user.get("name"),
        is_verified=user.get("is_verified", True),
        created_at=user["created_at"]
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_response)


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    users_collection = get_users_collection()
    user = users_collection.find_one({"_id": ObjectId(current_user["user_id"])})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        name=user.get("name"),
        created_at=user["created_at"]
    )


@app.put("/api/auth/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    users_collection = get_users_collection()
    user_id = ObjectId(current_user["user_id"])
    
    # Build update document
    update_data = {}
    if user_update.name is not None:
        update_data["name"] = user_update.name
    if user_update.password is not None:
        update_data["password"] = get_password_hash(user_update.password)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Update user
    result = users_collection.update_one(
        {"_id": user_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Return updated user
    updated_user = users_collection.find_one({"_id": user_id})
    return UserResponse(
        id=str(updated_user["_id"]),
        email=updated_user["email"],
        name=updated_user.get("name"),
        created_at=updated_user["created_at"]
    )


@app.delete("/api/auth/account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(current_user: dict = Depends(get_current_user)):
    """Delete user account and all associated scans"""
    users_collection = get_users_collection()
    scans_collection = get_scans_collection()
    user_id = ObjectId(current_user["user_id"])
    
    # Delete all user's scans
    scans_collection.delete_many({"user_id": str(user_id)})
    
    # Delete user account
    result = users_collection.delete_one({"_id": user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return None


# ==================== SCAN CRUD ENDPOINTS ====================

@app.post("/api/scans", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan_data: ScanCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new scan (analyze resume and save results)"""
    # Analyze resume using existing helper functions
    prompt = prepare_prompt(scan_data.resume_text, scan_data.job_description)
    response = get_gemini_response(prompt)
    result = json.loads(response)
    
    # Extract results
    ats_score = int(result.get("JD Match", 0))
    missing_keywords = result.get("MissingKeywords", [])
    matched_keywords = result.get("MatchedKeywords", [])
    profile_summary = result.get("Profile Summary", "")
    detailed_improvements = result.get("Detailed Improvements", [])
    quick_wins = result.get("Quick Wins", [])
    strengths = result.get("Strengths", [])
    
    # Save scan to database
    scans_collection = get_scans_collection()
    scan_doc = {
        "user_id": current_user["user_id"],
        "resume_text": scan_data.resume_text,
        "job_description": scan_data.job_description,
        "resume_filename": scan_data.resume_filename,
        "ats_score": ats_score,
        "missing_keywords": missing_keywords,
        "matched_keywords": matched_keywords,
        "ai_feedback": profile_summary,
        "detailed_improvements": detailed_improvements,
        "quick_wins": quick_wins,
        "strengths": strengths,
        "timestamp": datetime.utcnow()
    }
    
    result = scans_collection.insert_one(scan_doc)
    scan_id = str(result.inserted_id)
    
    return ScanResponse(
        id=scan_id,
        user_id=scan_doc["user_id"],
        resume_text=scan_doc["resume_text"],
        job_description=scan_doc["job_description"],
        resume_filename=scan_doc.get("resume_filename"),
        ats_score=scan_doc["ats_score"],
        missing_keywords=scan_doc["missing_keywords"],
        matched_keywords=scan_doc["matched_keywords"],
        ai_feedback=scan_doc["ai_feedback"],
        detailed_improvements=scan_doc.get("detailed_improvements", []),
        quick_wins=scan_doc.get("quick_wins", []),
        strengths=scan_doc.get("strengths", []),
        timestamp=scan_doc["timestamp"]
    )


@app.post("/api/scans/upload", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan_from_file(
    resume: UploadFile,
    jd: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Create a new scan from uploaded PDF file"""
    try:
        # Extract text from PDF
        resume_text = extract_pdf_text(resume.file)
        
        # Analyze resume
        prompt = prepare_prompt(resume_text, jd)
        response = get_gemini_response(prompt)
        result = json.loads(response)
        
        # Extract results
        ats_score = int(result.get("JD Match", 0))
        missing_keywords = result.get("MissingKeywords", [])
        matched_keywords = result.get("MatchedKeywords", [])
        profile_summary = result.get("Profile Summary", "")
        detailed_improvements = result.get("Detailed Improvements", [])
        quick_wins = result.get("Quick Wins", [])
        strengths = result.get("Strengths", [])
        
        # Save scan to database
        scans_collection = get_scans_collection()
        scan_doc = {
            "user_id": current_user["user_id"],
            "resume_text": resume_text,
            "job_description": jd,
            "resume_filename": resume.filename,
            "ats_score": ats_score,
            "missing_keywords": missing_keywords,
            "matched_keywords": matched_keywords,
            "ai_feedback": profile_summary,
            "detailed_improvements": detailed_improvements,
            "quick_wins": quick_wins,
            "strengths": strengths,
            "timestamp": datetime.utcnow()
        }
        
        result = scans_collection.insert_one(scan_doc)
        scan_id = str(result.inserted_id)
        
        return ScanResponse(
            id=scan_id,
            user_id=scan_doc["user_id"],
            resume_text=scan_doc["resume_text"],
            job_description=scan_doc["job_description"],
            resume_filename=scan_doc.get("resume_filename"),
            ats_score=scan_doc["ats_score"],
            missing_keywords=scan_doc["missing_keywords"],
            matched_keywords=scan_doc["matched_keywords"],
            ai_feedback=scan_doc["ai_feedback"],
            detailed_improvements=scan_doc.get("detailed_improvements", []),
            quick_wins=scan_doc.get("quick_wins", []),
            strengths=scan_doc.get("strengths", []),
            timestamp=scan_doc["timestamp"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing scan: {str(e)}"
        )


@app.get("/api/scans", response_model=ScanListResponse)
async def get_scans(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get all scans for the current user (lightweight summary without large text fields)"""
    try:
        scans_collection = get_scans_collection()
        
        # Find all scans for the user, sorted by timestamp (newest first)
        # Exclude large fields (resume_text, job_description, ai_feedback) from the query
        cursor = scans_collection.find(
            {"user_id": current_user["user_id"]},
            {
                "resume_text": 0,  # Exclude resume_text
                "job_description": 0,  # Exclude job_description
                "ai_feedback": 0  # Exclude ai_feedback
            }
        ).sort("timestamp", -1).skip(skip).limit(limit)
        
        scans = []
        for scan in cursor:
            scans.append(ScanSummary(
                id=str(scan["_id"]),
                user_id=scan["user_id"],
                resume_filename=scan.get("resume_filename"),
                ats_score=scan["ats_score"],
                missing_keywords=scan.get("missing_keywords", []),
                matched_keywords=scan.get("matched_keywords", []),
                timestamp=scan["timestamp"]
            ))
        
        # Get total count
        total = scans_collection.count_documents({"user_id": current_user["user_id"]})
        
        return ScanListResponse(scans=scans, total=total)
    except Exception as e:
        import traceback
        print(f"Error in get_scans endpoint: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading scans: {str(e)}"
        )


@app.get("/api/scans/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific scan by ID"""
    scans_collection = get_scans_collection()
    
    if not ObjectId.is_valid(scan_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid scan ID"
        )
    
    scan = scans_collection.find_one({
        "_id": ObjectId(scan_id),
        "user_id": current_user["user_id"]
    })
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    return ScanResponse(
        id=str(scan["_id"]),
        user_id=scan["user_id"],
        resume_text=scan["resume_text"],
        job_description=scan["job_description"],
        resume_filename=scan.get("resume_filename"),
        ats_score=scan["ats_score"],
        missing_keywords=scan["missing_keywords"],
        matched_keywords=scan["matched_keywords"],
        ai_feedback=scan["ai_feedback"],
        detailed_improvements=scan.get("detailed_improvements", []),
        quick_wins=scan.get("quick_wins", []),
        strengths=scan.get("strengths", []),
        timestamp=scan["timestamp"]
    )


@app.put("/api/scans/{scan_id}", response_model=ScanResponse)
async def update_scan(
    scan_id: str,
    scan_update: ScanUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a scan and re-analyze if needed"""
    scans_collection = get_scans_collection()
    
    if not ObjectId.is_valid(scan_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid scan ID"
        )
    
    # Get existing scan
    existing_scan = scans_collection.find_one({
        "_id": ObjectId(scan_id),
        "user_id": current_user["user_id"]
    })
    
    if not existing_scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    # Prepare updated data
    resume_text = scan_update.resume_text or existing_scan["resume_text"]
    job_description = scan_update.job_description or existing_scan["job_description"]
    
    # Re-analyze if resume or JD changed
    prompt = prepare_prompt(resume_text, job_description)
    response = get_gemini_response(prompt)
    result = json.loads(response)
    
    # Update scan document
    update_data = {
        "resume_text": resume_text,
        "job_description": job_description,
        "ats_score": int(result.get("JD Match", 0)),
        "missing_keywords": result.get("MissingKeywords", []),
        "matched_keywords": result.get("MatchedKeywords", []),
        "ai_feedback": result.get("Profile Summary", ""),
        "timestamp": datetime.utcnow()  # Update timestamp
    }
    
    if scan_update.resume_filename is not None:
        update_data["resume_filename"] = scan_update.resume_filename
    
    scans_collection.update_one(
        {"_id": ObjectId(scan_id)},
        {"$set": update_data}
    )
    
    # Return updated scan
    updated_scan = scans_collection.find_one({"_id": ObjectId(scan_id)})
    return ScanResponse(
        id=str(updated_scan["_id"]),
        user_id=updated_scan["user_id"],
        resume_text=updated_scan["resume_text"],
        job_description=updated_scan["job_description"],
        resume_filename=updated_scan.get("resume_filename"),
        ats_score=updated_scan["ats_score"],
        missing_keywords=updated_scan["missing_keywords"],
        matched_keywords=updated_scan["matched_keywords"],
        ai_feedback=updated_scan["ai_feedback"],
        detailed_improvements=updated_scan.get("detailed_improvements", []),
        quick_wins=updated_scan.get("quick_wins", []),
        strengths=updated_scan.get("strengths", []),
        timestamp=updated_scan["timestamp"]
    )


@app.delete("/api/scans/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(
    scan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a specific scan"""
    scans_collection = get_scans_collection()
    
    if not ObjectId.is_valid(scan_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid scan ID"
        )
    
    result = scans_collection.delete_one({
        "_id": ObjectId(scan_id),
        "user_id": current_user["user_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    return None


@app.delete("/api/scans", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_scans(current_user: dict = Depends(get_current_user)):
    """Delete all scans for the current user"""
    scans_collection = get_scans_collection()
    scans_collection.delete_many({"user_id": current_user["user_id"]})
    return None


# ==================== LEGACY ENDPOINT (for backward compatibility) ====================

@app.post("/analyze-resume/")
async def analyze_resume(resume: UploadFile, jd: str = Form(...)):
    """Legacy endpoint for resume analysis (without saving)"""
    try:
        print(f"Received request with JD: {jd[:50]}...")
        print(f"Resume filename: {resume.filename}")

        resume_text = extract_pdf_text(resume.file)
        print(f"Extracted resume text: {resume_text[:100]}...")

        prompt = prepare_prompt(resume_text, jd)
        print(f"Prepared prompt: {prompt[:100]}...")

        response = get_gemini_response(prompt)
        print(f"Got response: {response[:100]}...")

        result = json.loads(response)
        print(f"Parsed result: {result}")

        return result
    except Exception as e:
        print(f"Error in analyze_resume: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


@app.get("/test/")
async def test_endpoint():
    """Test endpoint"""
    return {"status": "ok", "message": "API is working"}
