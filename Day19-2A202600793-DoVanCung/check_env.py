import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("--- ENVIRONMENT CHECK ---")

# 1. Check libraries
try:
    import google.generativeai as genai
    print("[OK] google-generativeai is installed.")
except ImportError:
    print("[ERROR] google-generativeai is NOT installed.")

try:
    import networkx as nx
    print("[OK] networkx is installed.")
except ImportError:
    print("[ERROR] networkx is NOT installed.")

try:
    import pandas as pd
    print("[OK] pandas is installed.")
except ImportError:
    print("[ERROR] pandas is NOT installed.")

# 2. Check API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("[WARNING] GEMINI_API_KEY is not set in .env file or environment.")
elif api_key == "YOUR_GEMINI_API_KEY":
    print("[WARNING] GEMINI_API_KEY is still set to the placeholder 'YOUR_GEMINI_API_KEY'. Please replace it with your actual key.")
else:
    print("[OK] GEMINI_API_KEY is found (starts with: " + api_key[:6] + "...)")
    
    # 3. Test API Key connection
    try:
        genai.configure(api_key=api_key)
        # Using gemini-3.1-flash-lite
        model = genai.GenerativeModel('gemini-3.1-flash-lite')
        response = model.generate_content("Hello! Are you working?")
        print(f"[OK] Connection test to Gemini API succeeded. Response: '{response.text.strip()}'")
    except Exception as e:
        print(f"[ERROR] Failed to connect to Gemini API: {e}")
