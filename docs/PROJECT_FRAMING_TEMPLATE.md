# ATS Scanner 2.0 - Project Framing Template

## 1. PROJECT DESCRIPTION

**ATS Scanner 2.0** is an AI-powered resume optimization platform that analyzes resumes against job descriptions using Google's Gemini LLM. The tool provides job seekers with actionable insights to improve their resume's compatibility with Applicant Tracking Systems (ATS), increasing their chances of passing automated screening and landing interviews.

**Key Value Proposition:** Instant, AI-driven resume analysis that identifies missing keywords, highlights matched skills, and provides specific improvement suggestions tailored to each job application.

---

## 2. USER FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATED USER                           │
├─────────────────────────────────────────────────────────────────┤
│ 1. Sign Up / Login (Email + Password)                           │
│ 2. Email Verification (Optional - configurable)                 │
│ 3. Access Dashboard                                             │
│ 4. Perform Resume Analysis (same as above)                      │
│ 5. Click "Analyze & Save" to Store Results                      │
│ 6. View Scan History in Dashboard                               │
│ 7. Click on Past Scans to View Full Details                     │
│ 8. Delete Individual Scans or All Scans                         │
│ 9. Update Profile / Change Password                             │
│ 10. Delete Account (removes all associated scans)               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. USERS & CUSTOMERS

### **Target Users:**
- **Job Seekers** (Primary): Individuals actively applying for jobs who want to optimize their resumes for ATS systems
- **Career Changers**: People transitioning to new industries who need to tailor their resumes
- **Recent Graduates**: Entry-level candidates looking to improve their application materials

### **User Roles:**

1. **Guest User** - Must create account in order to analyze resumes.
2. **Registered User** - Can create an account, save scan history, and access past analyses
3. **Verified User** - Registered user who has verified their email.

### **Business Context:**
ATS Scanner 2.0 solves a critical pain point in the job search process. Applicant Tracking Systems automatically filter resumes based on keyword matching and formatting, causing many qualified candidates to be rejected before human review. This tool bridges that gap by providing AI-powered insights to help candidates optimize their resumes for ATS compatibility, ultimately improving their job search success rate.

---

## 4. CORE FUNCTIONS

### **Function 1: Resume Analysis Engine**
- **Purpose:** Analyze resume against job description using AI
- **Input:** Resume text (extracted from PDF) + Job description
- **Output:** ATS compatibility score (0-100%), matched keywords, missing keywords, profile summary
- **Technology:** Google Gemini 2.0 Flash LLM with structured JSON prompting
- **Impact:** Provides instant, AI-driven feedback on resume-to-job fit

### **Function 2: User Authentication & Account Management**
- **Purpose:** Secure user registration, login, and profile management
- **Features:** 
  - Email/password signup with optional email verification
  - JWT-based authentication
  - Password hashing with bcrypt
  - Profile updates (name, password)
  - Account deletion with cascade delete of all scans
- **Technology:** FastAPI, JWT tokens, bcrypt password hashing
- **Impact:** Enables users to save and track their scan history securely

### **Function 3: Scan History & Dashboard**
- **Purpose:** Store, retrieve, and manage user's past resume analyses
- **Features:**
  - Save scan results to MongoDB
  - View scan history with pagination
  - View detailed scan results (full resume, JD, feedback)
  - Delete individual or all scans
  - Sort by date (newest first)
- **Technology:** MongoDB collections, FastAPI CRUD endpoints
- **Impact:** Allows users to track progress and compare multiple job applications

### **Function 4: PDF Processing & Text Extraction**
- **Purpose:** Extract text from uploaded PDF resumes
- **Features:**
  - Parse multi-page PDFs
  - Extract and concatenate text from all pages
  - Error handling for corrupted/empty PDFs
- **Technology:** PyPDF2 library
- **Impact:** Enables users to upload resumes directly without manual copy-paste

---

## 5. SYSTEM ARCHITECTURE

### **3-Tier Architecture Diagram:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION TIER                            │
│                    (Frontend - Client)                          │
├─────────────────────────────────────────────────────────────────┤
│ • HTML5 / CSS3 / JavaScript (Vanilla)                           │
│ • Tailwind CSS (Styling)                                        │
│ • Bootstrap Icons (UI Icons)                                    │
│ • Responsive Design (Mobile-First)                              │
│                                                                 │
│ Pages: Landing, Login, Signup, Dashboard, Verification         │
│ Features: File upload, Form validation, Real-time feedback      │
└─────────────────────────────────────────────────────────────────┘
                              ↕
                    (HTTP/HTTPS REST API)
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION TIER                             │
│                    (Backend - Server)                           │
├─────────────────────────────────────────────────────────────────┤
│ • FastAPI (Web Framework)                                       │
│ • Python 3.12 (Runtime)                                         │
│ • Uvicorn (ASGI Server)                                         │
│                                                                 │
│ Core Modules:                                                   │
│ ├─ backend_api.py (Route handlers & endpoints)                  │
│ ├─ auth.py (JWT authentication & password hashing)              │
│ ├─ helper.py (LLM integration & PDF parsing)                    │
│ ├─ models.py (Pydantic data validation)                         │
│ ├─ database.py (MongoDB connection)                             │
│ └─ email_service.py (Email verification)                        │
│                                                                 │
│ Key Features:                                                   │
│ • RESTful API endpoints                                         │
│ • CORS middleware for frontend access                           │
│ • Request/response validation                                   │
│ • Error handling & logging                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↕
                    (MongoDB Wire Protocol)
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                    DATA TIER                                    │
│                    (Database - Persistence)                     │
├─────────────────────────────────────────────────────────────────┤
│ • MongoDB Atlas (Cloud Database)                                │
│ • Collections:                                                  │
│   ├─ users (User accounts & auth data)                          │
│   └─ scans (Resume analysis results)                            │
│                                                                 │
│ Features:                                                       │
│ • Document-based NoSQL storage                                  │
│ • Flexible schema for analysis results                          │
│ • Indexing for fast queries                                     │
│ • Cloud-hosted for scalability                                  │
└─────────────────────────────────────────────────────────────────┘
```

### **External Services:**

```
┌──────────────────────────────────────────────────────────────────┐
│                  EXTERNAL INTEGRATIONS                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Google Gemini 2.0 Flash LLM                                    │
│  ├─ Purpose: AI-powered resume analysis                         │
│  ├─ Input: Resume text + Job description                        │
│  └─ Output: Structured JSON analysis                            │
│                                                                  │
│  Gmail SMTP Server                                              │
│  ├─ Purpose: Send verification & welcome emails                 │
│  ├─ Configuration: SMTP_EMAIL, SMTP_PASSWORD                    │
│  └─ Features: HTML email templates                              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 6. TECHNOLOGY STACK

### **Frontend Tier:**
| Technology | Purpose | Why Chosen |
|-----------|---------|-----------|
| **HTML5** | Markup & Structure | Semantic, accessible web pages |
| **CSS3 / Tailwind CSS** | Styling & Layout | Rapid UI development, responsive design |
| **JavaScript (Vanilla)** | Interactivity & Logic | No build step needed, lightweight |
| **Bootstrap Icons** | UI Icons | Comprehensive icon library |

### **Application Tier:**
| Technology | Purpose | Why Chosen |
|-----------|---------|-----------|
| **Python 3.12** | Backend Language | Fast development, rich ecosystem |
| **FastAPI** | Web Framework | Modern, fast, automatic API docs, async support |
| **Uvicorn** | ASGI Server | High-performance async server |
| **Pydantic** | Data Validation | Type-safe request/response handling |
| **PyJWT** | JWT Authentication | Secure token-based auth |
| **Passlib + Bcrypt** | Password Security | Industry-standard password hashing |
| **PyPDF2** | PDF Processing | Extract text from PDF files |
| **google.generativeai** | LLM Integration | Access to Google Gemini API |
| **python-dotenv** | Config Management | Secure environment variable handling |

### **Data Tier:**
| Technology | Purpose | Why Chosen |
|-----------|---------|-----------|
| **MongoDB Atlas** | Database | NoSQL flexibility, cloud-hosted, scalable |
| **PyMongo** | MongoDB Driver | Official Python driver for MongoDB |

### **Deployment & DevOps:**
| Technology | Purpose | Why Chosen |
|-----------|---------|-----------|
| **Render** | Backend Hosting | Free tier, easy deployment, auto-scaling |
| **Vercel** | Frontend Hosting | Optimized for static sites, fast CDN |
| **Git/GitHub** | Version Control | Collaboration, CI/CD integration |

---

## 7. API ENDPOINTS SUMMARY

### **Authentication Endpoints:**
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/verify-email` - Verify email with code
- `POST /api/auth/resend-verification` - Resend verification code
- `GET /api/auth/me` - Get current user profile
- `PUT /api/auth/profile` - Update user profile
- `DELETE /api/auth/account` - Delete user account

### **Scan Endpoints:**
- `POST /api/scans` - Create scan (text input)
- `POST /api/scans/upload` - Create scan (PDF upload)
- `GET /api/scans` - Get all user's scans
- `GET /api/scans/{scan_id}` - Get specific scan details
- `PUT /api/scans/{scan_id}` - Update scan
- `DELETE /api/scans/{scan_id}` - Delete specific scan
- `DELETE /api/scans` - Delete all user's scans

### **Legacy Endpoints:**
- `POST /analyze-resume/` - Analyze without saving (backward compatibility)
- `GET /test/` - Health check

---

## 8. DATABASE SCHEMA

### **Users Collection:**
```javascript
{
  _id: ObjectId,
  email: String (unique),
  password: String (hashed),
  name: String (optional),
  is_verified: Boolean,
  verification_code: String (optional),
  code_expires_at: DateTime (optional),
  created_at: DateTime
}
```

### **Scans Collection:**
```javascript
{
  _id: ObjectId,
  user_id: String (reference to user._id),
  resume_text: String,
  job_description: String,
  resume_filename: String,
  ats_score: Number (0-100),
  missing_keywords: Array<String>,
  matched_keywords: Array<String>,
  ai_feedback: String,
  detailed_improvements: Array<Object>,
  quick_wins: Array<String>,
  strengths: Array<String>,
  timestamp: DateTime
}
```

---

## 9. KEY FEATURES

✅ **AI-Powered Analysis** - Google Gemini LLM for intelligent resume-to-job matching
✅ **Instant Feedback** - Real-time ATS score and keyword analysis
✅ **User Authentication** - Secure signup/login with JWT tokens
✅ **Email Verification** - Optional email verification for account security
✅ **Scan History** - Save and track all past resume analyses
✅ **Responsive Design** - Works on desktop, tablet, and mobile
✅ **PDF Support** - Upload resumes directly as PDF files
✅ **Detailed Insights** - Missing keywords, matched skills, improvement suggestions
✅ **Account Management** - Update profile, change password, delete account
✅ **RESTful API** - Clean, well-documented API endpoints

---

## 10. DEPLOYMENT ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER BROWSER                                 │
│              (Vercel Hosted Frontend)                           │
│         https://ats-scanner.vercel.app                          │
└─────────────────────────────────────────────────────────────────┘
                              ↕
                    (HTTPS REST API)
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                    RENDER BACKEND                               │
│              (FastAPI + Uvicorn Server)                         │
│         https://ats-2-point-0.onrender.com                      │
└─────────────────────────────────────────────────────────────────┘
                              ↕
                    (MongoDB Wire Protocol)
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                    MONGODB ATLAS                                │
│              (Cloud Database - Cluster)                         │
│         ats-scanner.mongodb.net                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. ENVIRONMENT VARIABLES

### **Backend (.env file):**
```
GOOGLE_API_KEY=your_google_gemini_api_key
MONGODB_URI=your_mongodb_atlas_connection_string
SECRET_KEY=your_jwt_secret_key
SMTP_EMAIL=your_gmail_address
SMTP_PASSWORD=your_gmail_app_password
EMAIL_VERIFICATION_ENABLED=true/false
```

---

## 12. FUTURE ENHANCEMENTS

- 📊 Analytics dashboard showing resume improvement trends
- 🔄 Resume version comparison (before/after)
- 💼 Job market insights and salary data
- 🤖 AI-powered resume rewriting suggestions
- 📱 Mobile app (React Native)
- 🌐 Multi-language support
- 🎯 Industry-specific resume templates
- 📧 Bulk email notifications for job matches
- 🔐 Two-factor authentication (2FA)
- 💳 Premium subscription tiers with advanced features

