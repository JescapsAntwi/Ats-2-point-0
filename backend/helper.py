import google.generativeai as genai
import PyPDF2 as pdf
import json

def configure_genai(api_key):
    """Configure the Generative AI API with error handling."""
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        raise Exception(f"Failed to configure Generative AI: {str(e)}")
    

def get_gemini_response(prompt):
    """Generate a response using Gemini with enhanced error handling and response validation."""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        
        # Ensure response is not empty
        if not response or not response.text:
            raise Exception("Empty response received from Gemini")
            
        # Try to parse the response as JSON
        try:
            response_json = json.loads(response.text)
            
            # Validate required fields
            required_fields = ["JD Match", "MissingKeywords", "MatchedKeywords", "Profile Summary"]
            for field in required_fields:
                if field not in response_json:
                    raise ValueError(f"Missing required field: {field}")
            
            # Optional fields for enhanced feedback
            optional_fields = ["Detailed Improvements", "Quick Wins", "Strengths"]
            for field in optional_fields:
                if field not in response_json:
                    response_json[field] = []
                    
            return response.text
            
        except json.JSONDecodeError:
            # If response is not valid JSON, try to extract JSON-like content
            import re
            json_pattern = r'\{.*\}'
            match = re.search(json_pattern, response.text, re.DOTALL)
            if match:
                return match.group()
            else:
                raise Exception("Could not extract valid JSON response")
                
    except Exception as e:
        raise Exception(f"Error generating response: {str(e)}")

def extract_pdf_text(uploaded_file):
    """Extract text from PDF with enhanced error handling."""
    try:
        reader = pdf.PdfReader(uploaded_file)
        if len(reader.pages) == 0:
            raise Exception("PDF file is empty")
            
        text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
                
        if not text:
            raise Exception("No text could be extracted from the PDF")
            
        return " ".join(text)
        
    except Exception as e:
        raise Exception(f"Error extracting PDF text: {str(e)}")
    


def prepare_prompt(resume_text, job_description):
    """Prepare the input prompt with improved structure and validation."""
    if not resume_text or not job_description:
        raise ValueError("Resume text and job description cannot be empty")
        
    prompt_template = """
    Act as an expert ATS (Applicant Tracking System) specialist and career coach with deep expertise in:
    - Technical recruiting and ATS optimization
    - Software engineering, data science, and tech roles
    - Resume writing and keyword optimization
    - Industry best practices for job applications
    
    Your task: Analyze this resume against the job description and provide actionable, specific improvement suggestions.
    
    Resume:
    {resume_text}
    
    Job Description:
    {job_description}

    CRITICAL: Respond ONLY with valid JSON. No markdown, no code blocks, no explanations outside the JSON.

    Provide your analysis in this EXACT JSON format:
    {{
        "JD Match": "percentage between 0-100 as a number",
        "MissingKeywords": ["keyword1", "keyword2", "keyword3", ...],
        "MatchedKeywords": ["keyword1", "keyword2", "keyword3", ...],
        "Profile Summary": "2-3 sentence overview of the candidate's profile and overall match quality",
        "Detailed Improvements": [
            {{
                "category": "Keywords & Skills",
                "issue": "Specific problem identified",
                "suggestion": "Detailed, actionable recommendation with examples",
                "impact": "How this will improve ATS score",
                "priority": "High/Medium/Low"
            }},
            {{
                "category": "Experience & Achievements",
                "issue": "Specific problem identified",
                "suggestion": "Detailed, actionable recommendation with examples",
                "impact": "How this will improve ATS score",
                "priority": "High/Medium/Low"
            }},
            {{
                "category": "Format & Structure",
                "issue": "Specific problem identified",
                "suggestion": "Detailed, actionable recommendation",
                "impact": "How this will improve ATS score",
                "priority": "High/Medium/Low"
            }}
        ],
        "Quick Wins": [
            "Immediate action item 1 that can boost score quickly",
            "Immediate action item 2 that can boost score quickly",
            "Immediate action item 3 that can boost score quickly"
        ],
        "Strengths": [
            "What the resume does well",
            "Strong points to maintain"
        ]
    }}

    IMPORTANT GUIDELINES:
    1. Be specific - mention exact keywords, skills, or phrases to add
    2. Provide examples where possible (e.g., "Add 'Python, Django, REST APIs' to skills section")
    3. Prioritize improvements by impact (High priority = biggest ATS score boost)
    4. Focus on ATS optimization, not just general resume advice
    5. Identify at least 3-5 detailed improvements across different categories
    6. Quick Wins should be simple changes that take <5 minutes each
    7. Missing keywords should include technical skills, tools, methodologies, and industry terms from the JD
    8. Consider synonyms and related terms (e.g., if JD mentions "JavaScript", also check for "JS", "React", "Node.js")
    """
    
    return prompt_template.format(
        resume_text=resume_text.strip(),
        job_description=job_description.strip()
    )

