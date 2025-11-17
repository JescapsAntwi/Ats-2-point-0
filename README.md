

# ATS Scanner 2.0

🚀 An AI-powered tool that analyzes resumes against job descriptions using Large Language Models (LLMs) to help job seekers optimize their applications for Applicant Tracking Systems (ATS).

---

## 🧠 Features

- 📄 Upload your resume (PDF format)
- 📝 Paste a job description
- 🤖 Powered by Google Gemini LLM for smart matching
- 🔍 Get:
  - ATS Compatibility Score
  - Missing and Matched Keywords
  - Profile Summary in bullet points
  - Tailored improvement suggestions
- ⚡ Instant analysis with a clean, responsive UI
- 🎨 Beautiful frontend built with Tailwind CSS

---

## 📁 Project Structure

```
ATS_Scanner/
│
├── backend/                  # FastAPI backend
│   ├── __init__.py          # Package initializer
│   ├── backend_api.py       # Main API routes and endpoints
│   ├── auth.py              # Authentication logic (JWT, password hashing)
│   ├── database.py          # MongoDB connection and operations
│   ├── helper.py            # LLM prompt logic + PDF parsing
│   └── models.py            # Pydantic models for request/response
│
├── frontend/                # Static HTML/CSS/JS frontend
│   ├── index.html           # Landing page with resume scanner
│   ├── dashboard.html       # User dashboard with scan history
│   ├── login.html           # User login page
│   ├── signup.html          # User registration page
│   ├── auth.js              # Authentication utilities
│   ├── dashboard.js         # Dashboard functionality
│   ├── script.js            # Main page scripts
│   └── styles.css           # Global styles
│
├── docs/                    # Documentation
│   ├── MONGODB_SETUP.md     # MongoDB Atlas setup guide
│   ├── SETUP.md             # Project setup instructions
│   └── sample.pdf           # Sample resume for testing
│
├── tests/                   # Test files
│
├── venv312/                 # Python virtual environment
│
├── .env                     # Environment variables (API keys, DB connection)
├── .gitignore               # Git ignore rules
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
└── start_server.sh          # Server startup script
```

---

## 🛠 Tech Stack

- **Frontend**: HTML, Tailwind CSS, Bootstrap Icons
- **Backend**: Python, FastAPI
- **Database**: MongoDB
- **AI Integration**: Google Gemini via `google.generativeai`
- **PDF Parsing**: PyPDF2

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone git@github.com:jescapsantwi/ATS-2-point-0.git
cd ATS-2-point-0
```

### 2. Set up a virtual environment

```bash
python -m venv ats-env
```

**Activate it:**

- **Windows**  
  `ats-env\Scripts\activate`

- **macOS/Linux**  
  `source ats-env/bin/activate`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Google Gemini API key

Create a `.env` file inside the `backend/` folder:

```ini
GOOGLE_API_KEY=your_api_key_here
```

> ⚠️ Do not share your API key publicly.

### 5. Run the FastAPI backend server

```bash
cd backend
uvicorn backend_api:app --reload
```

### 6. Use the Web UI

Open `frontend/index.html` directly in your browser.

---

## 📸 Screenshots

### Landing Page
![ATS Scanner Landing Page](docs/images/ats-scanner-2-landing.png)

The main interface allows users to paste job descriptions and upload their resume PDFs for instant AI-powered analysis.


---

## 📬 Contact

Made with ❤️ by [Jescaps Antwi](https://github.com/JescapsAntwi)  
For any inquiries or collaborations, feel free to reach out via LinkedIn or email.

---

