# ATS Scanner - CRUD Implementation Setup Guide

## Overview
This project now includes full CRUD (Create, Read, Update, Delete) operations for user management and resume scan history.

## Features Implemented

### 1. User Management (CRUD)
- ✅ **Create**: User registration (signup)
- ✅ **Read**: User login and profile viewing
- ✅ **Update**: Profile management (name, password)
- ✅ **Delete**: Account deletion

### 2. Resume & Scan Management (CRUD)
- ✅ **Create**: Save new scans after analysis
- ✅ **Read**: View scan history in dashboard
- ✅ **Update**: Edit and rescan saved resumes
- ✅ **Delete**: Delete individual scans or clear all history

### 3. Authentication
- ✅ JWT-based authentication
- ✅ Secure password hashing with bcrypt
- ✅ Protected API endpoints

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```env
MONGODB_URI=your_mongodb_atlas_connection_string
GOOGLE_API_KEY=your_google_api_key
SECRET_KEY=your-secret-key-for-jwt
```

**Getting MongoDB Atlas URI:**
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Go to "Database Access" and create a user
4. Go to "Network Access" and add your IP (or 0.0.0.0/0 for development)
5. Click "Connect" on your cluster and copy the connection string
6. Replace `<password>` with your user password

**Getting Google API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

**Generating SECRET_KEY:**
```bash
openssl rand -hex 32
```

### 3. Start the Backend Server

**Important:** Run uvicorn from the project root directory (not from inside the `backend` folder):

```bash
# From the project root directory (ATS_Scanner/)
uvicorn backend.backend_api:app --reload --port 8000
```

**Alternative:** If you're in the backend directory, you can run:
```bash
cd ..  # Go back to project root
uvicorn backend.backend_api:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### 4. Open the Frontend

Simply open `frontend/index.html` in your web browser, or use a local server:

```bash
# Using Python
cd frontend
python -m http.server 8080

# Using Node.js (if you have http-server installed)
npx http-server -p 8080
```

Then navigate to `http://localhost:8080`

## API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user profile
- `PUT /api/auth/profile` - Update user profile
- `DELETE /api/auth/account` - Delete user account

### Scans
- `POST /api/scans` - Create scan (with resume text)
- `POST /api/scans/upload` - Create scan (with PDF file upload)
- `GET /api/scans` - Get all scans for current user
- `GET /api/scans/{scan_id}` - Get specific scan
- `PUT /api/scans/{scan_id}` - Update and rescan
- `DELETE /api/scans/{scan_id}` - Delete specific scan
- `DELETE /api/scans` - Delete all scans

### Legacy
- `POST /analyze-resume/` - Legacy endpoint (no authentication required)

## Frontend Pages

1. **index.html** - Main page with resume scanner
2. **signup.html** - User registration
3. **login.html** - User login
4. **dashboard.html** - View scan history

## Database Schema

### Users Collection
```json
{
  "_id": ObjectId,
  "email": "user@example.com",
  "password": "hashed_password",
  "name": "User Name",
  "created_at": ISODate
}
```

### Scans Collection
```json
{
  "_id": ObjectId,
  "user_id": "user_id_string",
  "resume_text": "extracted resume text",
  "job_description": "job description text",
  "resume_filename": "resume.pdf",
  "ats_score": 85,
  "missing_keywords": ["keyword1", "keyword2"],
  "matched_keywords": ["keyword3", "keyword4"],
  "ai_feedback": "Profile summary and suggestions",
  "timestamp": ISODate
}
```

## Usage Flow

1. **Sign Up**: Create a new account at `/signup.html`
2. **Login**: Login at `/login.html`
3. **Scan Resume**: 
   - Go to main page
   - Enter job description
   - Upload PDF resume
   - Click "Analyze & Save" to save results
4. **View History**: Go to Dashboard to see all past scans
5. **Manage Scans**: View details, update, or delete scans from dashboard

## Security Notes

- Passwords are hashed using bcrypt
- JWT tokens expire after 7 days
- All scan endpoints require authentication
- CORS is currently set to allow all origins (change for production)

## Troubleshooting

**MongoDB Connection Error:**
- Verify your MongoDB Atlas URI is correct
- Check that your IP is whitelisted in Network Access
- Ensure your database user has proper permissions

**Authentication Errors:**
- Clear browser localStorage and try logging in again
- Check that SECRET_KEY is set in `.env`
- Verify JWT token hasn't expired

**PDF Upload Issues:**
- Ensure file is a valid PDF
- Check file size limits
- Verify backend server is running

## Next Steps

For production deployment:
1. Change CORS settings to specific domain
2. Use environment-specific SECRET_KEY
3. Set up proper error logging
4. Add rate limiting
5. Implement email verification
6. Add password reset functionality

