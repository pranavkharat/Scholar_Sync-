import os
import requests
from dotenv import load_dotenv

# Load your key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env")
    exit()

print(f"Checking models for API Key: {api_key[:5]}...")

# Hit the Google API endpoint directly
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)

if response.status_code == 200:
    print("\nSUCCESS! Your key is valid. Here are your available models:\n")
    data = response.json()
    for model in data.get('models', []):
        # We only care about models that support 'generateContent'
        if "generateContent" in model.get("supportedGenerationMethods", []):
            print(f"-> {model['name']}")
            
    print("\nINSTRUCTION: Copy one of the names above (e.g., 'models/gemini-pro')")
    print("and use it in your main.py (remove the 'models/' prefix).")
else:
    print(f"\nFAILURE. Status Code: {response.status_code}")
    print(f"Error Message: {response.text}")