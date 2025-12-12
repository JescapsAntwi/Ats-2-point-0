# ATS Scanner 2.0 - Complete UML Reference Guide

## Overview
This document contains all UML diagrams for the ATS Scanner 2.0 project in PlantUML format. You can use these diagrams to generate visual representations on PlantUML online editor or integrate them into your documentation.

---

## 1. DATABASE SCHEMA UML (UML_DIAGRAM.puml)

This diagram shows the MongoDB collections and their relationships.

**Key Entities:**
- **Users Collection** - Stores user account information
- **Scans Collection** - Stores resume analysis results
- **AnalysisResult** - Structure of AI analysis output
- **Improvement** - Detailed improvement suggestions

**Relationships:**
- One User has Many Scans (1:*)
- One Scan contains One AnalysisResult (1:1)
- One AnalysisResult includes Many Improvements (1:*)

**How to Use:**
1. Go to https://www.plantuml.com/plantuml/uml/
2. Copy the content from `UML_DIAGRAM.puml`
3. Paste into the editor
4. Click "Submit" to generate the diagram
5. Export as PNG/SVG for presentations

---

## 2. SYSTEM ARCHITECTURE UML (SYSTEM_ARCHITECTURE_UML.puml)

This diagram shows the complete system architecture with all components and their interactions.

**Three Tiers:**

### Presentation Tier (Frontend)
- Landing Page, Login, Signup, Dashboard, Verification pages
- JavaScript modules (auth.js, script.js, dashboard.js)
- Styling (Tailwind CSS, Bootstrap Icons)

### Application Tier (Backend)
- API Gateway with CORS middleware
- Authentication Module (JWT, password hashing, email verification)
- API Endpoints (Auth, Scans, Legacy)
- Business Logic (LLM integration, PDF parsing, validation)
- Data Access Layer (MongoDB connection)

### Data Tier (Database)
- MongoDB Atlas with users and scans collections

### External Services
- Google Gemini 2.0 Flash LLM
- Gmail SMTP for email verification

**How to Use:**
1. Go to https://www.plantuml.com/plantuml/uml/
2. Copy the content from `SYSTEM_ARCHITECTURE_UML.puml`
3. Paste into the editor
4. Click "Submit" to generate the diagram
5. Use for architecture documentation and presentations

---

## 3. API DATA FLOW UML (API_DATA_FLOW_UML.puml)

This diagram shows the API request/response models and data flow.

**Request Models:**
- UserCreateRequest - Signup data
- UserLoginRequest - Login credentials
- VerifyEmailRequest - Email verification
- ScanCreateRequest - Text-based analysis
- ScanUploadRequest - PDF-based analysis

**Response Models:**
- UserResponse - User data
- TokenResponse - JWT token + user
- ScanResponse - Full scan details
- ScanSummary - Lightweight scan info
- ScanListResponse - List of scans
- AnalysisResponse - LLM analysis output
- Improvement - Detailed suggestions

**Data Flow:**
- Requests flow through validation
- Responses contain structured data
- Analysis results include improvements

**How to Use:**
1. Go to https://www.plantuml.com/plantuml/uml/
2. Copy the content from `API_DATA_FLOW_UML.puml`
3. Paste into the editor
4. Click "Submit" to generate the diagram
5. Reference for API documentation

---

## 4. DETAILED ENTITY RELATIONSHIPS

### Users Collection Schema
```json
{
  "_id": "ObjectId (Primary Key)",
  "email": "String (Unique, Required)",
  "password": "String (Hashed, Required)",
  "name": "String (Optional)",
  "is_verified": "Boolean (Default: false)",
  "verification_code": "String (Optional, 6 digits)",
  "code_expires_at": "DateTime (Optional, 15 min expiry)",
  "created_at": "DateTime (Auto-generated)"
}
```

**Indexes:**
- `email` (unique)
- `created_at` (for sorting)

**Methods:**
- `create_user()` - Create new user account
- `verify_email()` - Mark email as verified
- `update_profile()` - Update user information
- `delete_account()` - Delete user and cascade delete scans

---

### Scans Collection Schema
```json
{
  "_id": "ObjectId (Primary Key)",
  "user_id": "String (Foreign Key to Users._id)",
  "resume_text": "String (Full resume content)",
  "job_description": "String (Full job posting)",
  "resume_filename": "String (Optional, original filename)",
  "ats_score": "Number (0-100, ATS compatibility %)",
  "missing_keywords": "Array<String> (Keywords in JD but not resume)",
  "matched_keywords": "Array<String> (Keywords in both)",
  "ai_feedback": "String (Profile summary from LLM)",
  "detailed_improvements": "Array<Improvement> (Structured suggestions)",
  "quick_wins": "Array<String> (Fast improvement actions)",
  "strengths": "Array<String> (What resume does well)",
  "timestamp": "DateTime (When analysis was performed)"
}
```

**Indexes:**
- `user_id` (for filtering by user)
- `timestamp` (for sorting)
- `ats_score` (for filtering by score)

**Methods:**
- `create_scan()` - Create new analysis
- `get_scan_details()` - Retrieve full scan
- `update_scan()` - Re-analyze and update
- `delete_scan()` - Remove scan

---

### Improvement Object Schema
```json
{
  "category": "String (Keywords & Skills | Experience & Achievements | Format & Structure)",
  "issue": "String (Specific problem identified)",
  "suggestion": "String (Detailed, actionable recommendation)",
  "impact": "String (How this improves ATS score)",
  "priority": "String (High | Medium | Low)"
}
```

---

## 5. API ENDPOINT MAPPING

### Authentication Endpoints

**POST /api/auth/signup**
- Request: UserCreateRequest
- Response: { message, email, user_id, requires_verification, access_token?, user? }
- Status: 201 Created

**POST /api/auth/login**
- Request: UserLoginRequest
- Response: TokenResponse
- Status: 200 OK

**POST /api/auth/verify-email**
- Request: VerifyEmailRequest
- Response: TokenResponse
- Status: 200 OK

**POST /api/auth/resend-verification**
- Request: ResendVerification
- Response: { message, email }
- Status: 200 OK

**GET /api/auth/me**
- Request: (Requires Bearer token)
- Response: UserResponse
- Status: 200 OK

**PUT /api/auth/profile**
- Request: UserUpdate
- Response: UserResponse
- Status: 200 OK

**DELETE /api/auth/account**
- Request: (Requires Bearer token)
- Response: (No content)
- Status: 204 No Content

---

### Scan Endpoints

**POST /api/scans**
- Request: ScanCreateRequest
- Response: ScanResponse
- Status: 201 Created
- Auth: Required

**POST /api/scans/upload**
- Request: ScanUploadRequest (multipart/form-data)
- Response: ScanResponse
- Status: 201 Created
- Auth: Required

**GET /api/scans**
- Query Params: skip (default: 0), limit (default: 50)
- Response: ScanListResponse
- Status: 200 OK
- Auth: Required

**GET /api/scans/{scan_id}**
- Response: ScanResponse
- Status: 200 OK
- Auth: Required

**PUT /api/scans/{scan_id}**
- Request: ScanUpdate
- Response: ScanResponse
- Status: 200 OK
- Auth: Required

**DELETE /api/scans/{scan_id}**
- Response: (No content)
- Status: 204 No Content
- Auth: Required

**DELETE /api/scans**
- Response: (No content)
- Status: 204 No Content
- Auth: Required

---

### Legacy Endpoints

**POST /analyze-resume/**
- Request: multipart/form-data (resume, jd)
- Response: AnalysisResponse
- Status: 200 OK
- Auth: Not required

**GET /test/**
- Response: { status, message }
- Status: 200 OK
- Auth: Not required

---

## 6. DATA FLOW DIAGRAMS

### User Registration Flow
```
User Input (email, password, name)
    ↓
Validation (Pydantic)
    ↓
Check if email exists
    ↓
Hash password (bcrypt)
    ↓
Create user in MongoDB
    ↓
Generate verification code (if enabled)
    ↓
Send verification email (if enabled)
    ↓
Return response (with token if no verification)
```

### Resume Analysis Flow
```
User Input (resume, job description)
    ↓
Validate input
    ↓
Extract PDF text (if file upload)
    ↓
Prepare LLM prompt
    ↓
Send to Google Gemini API
    ↓
Parse JSON response
    ↓
Validate response structure
    ↓
Save to MongoDB (if authenticated)
    ↓
Return analysis results
```

### Authentication Flow
```
User Login (email, password)
    ↓
Find user in MongoDB
    ↓
Verify password (bcrypt)
    ↓
Check email verification status
    ↓
Generate JWT token
    ↓
Return token + user data
    ↓
Client stores token in localStorage
    ↓
Include token in Authorization header for future requests
```

---

## 7. GENERATING UML DIAGRAMS

### Online PlantUML Editor
1. Visit: https://www.plantuml.com/plantuml/uml/
2. Copy UML code from .puml files
3. Paste into editor
4. Click "Submit"
5. Export as PNG/SVG

### Command Line (if PlantUML installed)
```bash
# Install PlantUML
brew install plantuml

# Generate PNG from .puml file
plantuml UML_DIAGRAM.puml -o output_folder

# Generate SVG
plantuml -tsvg UML_DIAGRAM.puml -o output_folder
```

### VS Code Extension
1. Install "PlantUML" extension
2. Open .puml file
3. Right-click → "Preview Current Diagram"
4. Export from preview

---

## 8. CUSTOMIZING UML DIAGRAMS

### Color Scheme
```plantuml
skinparam backgroundColor #FAF9F6
skinparam classBackgroundColor #FFFFFF
skinparam classBorderColor #1E3A8A
skinparam classArrowColor #312E81
skinparam noteBkgColor #FDB813
skinparam noteBorderColor #DAA520
```

### Font Customization
```plantuml
skinparam defaultFontName Poppins
skinparam defaultFontSize 12
```

### Adding New Elements
```plantuml
class NewEntity {
    field1: Type
    field2: Type
    --
    method1()
    method2()
}

NewEntity --> ExistingEntity : relationship
```

---

## 9. PRESENTATION TIPS

### For PowerPoint
1. Export UML diagrams as PNG (high resolution)
2. Insert into slides
3. Add captions and annotations
4. Use consistent color scheme

### For Documentation
1. Export as SVG for scalability
2. Embed in markdown files
3. Link to PlantUML online editor
4. Include descriptions

### For Technical Discussions
1. Use online editor for live editing
2. Share link with team
3. Collaborate on diagram improvements
4. Version control .puml files in Git

---

## 10. QUICK REFERENCE

### Key Relationships
- **1:* (One-to-Many):** One user has many scans
- **1:1 (One-to-One):** One scan has one analysis result
- **Foreign Key:** user_id in scans references users._id

### Important Fields
- **_id:** MongoDB ObjectId (auto-generated)
- **user_id:** Links scans to users
- **ats_score:** 0-100 percentage
- **timestamp:** When analysis was performed
- **is_verified:** Email verification status

### API Authentication
- **Method:** Bearer token (JWT)
- **Header:** `Authorization: Bearer <token>`
- **Expiry:** 7 days
- **Encoding:** HS256

### Error Handling
- **400:** Bad Request (validation error)
- **401:** Unauthorized (missing/invalid token)
- **403:** Forbidden (email not verified)
- **404:** Not Found (resource doesn't exist)
- **500:** Internal Server Error

---

## 11. INTEGRATION CHECKLIST

- [ ] Database schema created in MongoDB
- [ ] Collections indexed for performance
- [ ] API endpoints tested with Postman
- [ ] Authentication flow verified
- [ ] Email service configured
- [ ] LLM integration tested
- [ ] PDF parsing tested
- [ ] Frontend connected to backend
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Security headers added
- [ ] CORS configured
- [ ] Rate limiting implemented
- [ ] Monitoring set up
- [ ] Backup strategy defined

---

## 12. TROUBLESHOOTING

### Common Issues

**Issue:** UML diagram not rendering
- **Solution:** Check PlantUML syntax, ensure no special characters

**Issue:** Database connection failing
- **Solution:** Verify MONGODB_URI in .env file

**Issue:** API endpoints returning 401
- **Solution:** Ensure token is included in Authorization header

**Issue:** Email verification not working
- **Solution:** Check SMTP credentials and Gmail app password

**Issue:** LLM analysis taking too long
- **Solution:** Optimize prompt, check API rate limits

---

## 13. RESOURCES

- **PlantUML Documentation:** https://plantuml.com/
- **MongoDB Documentation:** https://docs.mongodb.com/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Google Gemini API:** https://ai.google.dev/
- **JWT Documentation:** https://jwt.io/

---

## 14. VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-12 | Initial UML diagrams created |
| 1.1 | TBD | Add sequence diagrams |
| 1.2 | TBD | Add deployment diagrams |
| 2.0 | TBD | Add state machine diagrams |

---

**Last Updated:** December 12, 2025
**Created by:** Jescaps Antwi
**Project:** ATS Scanner 2.0

