# AI Resume Screener

A modern, AI-powered Resume Screener built with a FastAPI backend and a premium glassmorphic HTML/JS frontend. It extracts text from PDF and DOCX resumes and analyzes them against a job description using the Gemini API.

## Features
- **Dynamic Frontend:** Premium UI with animations, progress bars, and glassmorphism.
- **FastAPI Backend:** High-performance async API.
- **Gemini API Integration:** Uses `gemini-flash-latest` for strict JSON evaluation of candidates.

## Local Development Setup

1. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   # Activate on Windows:
   .\venv\Scripts\activate
   # Activate on macOS/Linux:
   source venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables:**
   Create a `.env` file in the root directory and add your Gemini API Key:
   ```text
   GEMINI_API_KEY=your_actual_api_key
   ```

4. **Run the Server:**
   ```bash
   uvicorn main:app --reload
   ```
   Open `http://localhost:8000` in your browser.

## Deployment to Render (Recommended)

This repository is ready to be deployed directly to Render as a Web Service.

1. Push this repository to GitHub.
2. In the Render Dashboard, create a new **Web Service**.
3. Connect your GitHub repository.
4. Set the Environment to **Python**.
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Add an Environment Variable in the Render dashboard:
   - Key: `GEMINI_API_KEY`
   - Value: `your_actual_api_key`
8. Click Deploy!
