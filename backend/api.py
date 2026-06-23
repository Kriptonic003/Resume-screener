import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.screener import extract_text, screen_resume

router = APIRouter()

@router.post("/scan")
async def scan_endpoint(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    if not resume:
        raise HTTPException(status_code=400, detail="No resume file provided")
    
    # Save uploaded file temporarily
    temp_file_path = f"temp_{resume.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)
            
        # Extract text
        print(f"Extracting text from {resume.filename}...")
        resume_text = extract_text(temp_file_path, resume.filename)
        
        if not resume_text.strip():
            print("Extracted text is empty.")
            raise HTTPException(status_code=400, detail="Could not extract text from the file")
            
        # Call Anthropic API
        print("Sending prompt to Gemini API...")
        result = screen_resume(resume_text, job_description)
        print("Received response from Gemini API!")
        
        return result
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
