import requests
import os

# URL of the API endpoint
url = "http://localhost:8000/analyze-resume/"

# Sample job description
job_description = "We are looking for a Python developer with experience in FastAPI and Streamlit."

# Path to a sample PDF file
pdf_path = "sample.pdf"

# Create a sample PDF file if it doesn't exist
if not os.path.exists(pdf_path):
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 750, "Sample Resume")
    c.drawString(100, 700, "Python Developer with 5 years of experience")
    c.drawString(100, 650, "Skills: Python, FastAPI, Streamlit, React")
    c.save()

# Prepare the form data
files = {"resume": open(pdf_path, "rb")}
data = {"jd": job_description}

# Make the request
try:
    response = requests.post(url, files=files, data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")
