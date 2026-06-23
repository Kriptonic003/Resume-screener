import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(override=True)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

for m in ['gemini-2.0-flash', 'gemini-flash-latest', 'gemini-2.0-flash-lite', 'gemini-pro-latest']:
    print(f"\nTesting {m}...")
    try:
        model = genai.GenerativeModel(m)
        resp = model.generate_content("hello, are you working?")
        print(f"Success: {resp.text.strip()}")
        break # If one works, we are good!
    except Exception as e:
        print(f"Error: {e}")
