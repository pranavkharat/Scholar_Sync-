from openai import OpenAI
import os
from dotenv import load_dotenv
import sys

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("❌ No OPENAI_API_KEY found in .env")
    sys.exit(1)

print(f"🔑 API Key found: {api_key[:10]}...")
print("🔄 Testing OpenAI connection with timeout...")

try:
    client = OpenAI(
        api_key=api_key,
        timeout=15.0,
        max_retries=2
    )
    
    print("📡 Sending test request...")
    
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Say hello in 3 words'}],
        max_tokens=10,
        timeout=15.0
    )
    
    print('✅ OpenAI works!')
    print(f'Response: {response.choices[0].message.content}')
    
except Exception as e:
    print(f'❌ Error: {type(e).__name__}: {str(e)}')
    import traceback
    traceback.print_exc()


