import os
import json
import pdfplumber
import docx
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(override=True)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting PDF: {e}")
    return text

def extract_text_from_docx(file_path: str) -> str:
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
    return text

def extract_text(file_path: str, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif filename.lower().endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        # Fallback for text files
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""

def screen_resume(resume_text: str, job_description: str) -> dict:
    prompt = f"""
    You are an expert HR recruiter and ATS (Applicant Tracking System).
    Analyze the provided resume against the job description.
    
    Job Description:
    {job_description}
    
    Resume:
    {resume_text}
    
    Return a strict JSON object with the following schema:
    {{
      "overall_fit": (integer between 0 and 100),
      "skills_match": (integer between 0 and 100),
      "experience_match": (integer between 0 and 100),
      "keyword_score": (integer between 0 and 100),
      "skill_breakdown": [
        {{"skill": "skill_name", "score": (integer between 0 and 100)}}
      ],
      "keywords": [
        {{"word": "keyword", "status": "matched" | "partial" | "missing"}}
      ],
      "recommendation": "2-3 sentences of improvement advice."
    }}
    
    Ensure your entire response is just the JSON object. Do not include markdown formatting or any other text.
    """
    
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1,
            )
        )
        
        # Parse the JSON response
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        return json.loads(response_text)
    except Exception as e:
        print(f"Error calling Gemini or parsing JSON: {e}")
        return {
            "overall_fit": 0,
            "skills_match": 0,
            "experience_match": 0,
            "keyword_score": 0,
            "skill_breakdown": [{"skill": "Error Processing", "score": 0}],
            "keywords": [{"word": "Error", "status": "missing"}],
            "recommendation": f"Failed to analyze resume. Error: {str(e)}"
        }
