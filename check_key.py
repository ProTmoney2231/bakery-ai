from dotenv import load_dotenv
from openai import OpenAI
import os

# Load .env file
load_dotenv()

# Get API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ No API key found. Make sure your .env file has: 
OPENAI_API_KEY=sk-...")
    exit(1)

print("✅ API key loaded (hidden for security)")

# Initialize client
client = OpenAI(api_key=api_key)

# Test API request
try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello, are you 
working?"}],
        max_tokens=20
    )
    print("✅ API request successful:", 
response.choices[0].message.content)
except Exception as e:
    print("❌ API request failed:", str(e))

