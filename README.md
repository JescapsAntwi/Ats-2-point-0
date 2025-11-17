

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
ATS-Scanner/
│
├── backend/                  # FastAPI backend
│   ├── backend_api.py        # API route for analysis
│   └── helper.py             # LLM prompt logic + PDF parsing
│
├── frontend/                 # Static HTML frontend
│   └── index.html            # User interface
│
├── requirements.txt          # Python dependencies
└── .gitignore                # Ignore env files and unnecessary folders
```

---

## 🛠 Tech Stack

- **Frontend**: HTML, Tailwind CSS, Bootstrap Icons
- **Backend**: Python, FastAPI
- **AI Integration**: Google Gemini via `google.generativeai`
- **PDF Parsing**: PyPDF2

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone git@github.com:VishalPatil54/ATS-Scanner.git
cd ATS-Scanner
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

![image](https://github.com/user-attachments/assets/6ee23bfc-617e-43ec-af1f-5acf47b2c82a)


---

## 📬 Contact

Made with ❤️ by [Vishal Patil](https://github.com/VishalPatil54)  
For any inquiries or collaborations, feel free to reach out via LinkedIn or email.

---

