import os
from dotenv import load_dotenv
from openai import OpenAI

# Load your .env file
load_dotenv()

# Get the API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env")

# Initialize client
client = OpenAI(api_key=api_key)

# Test: Call OpenAI with a simple prompt
response = client.chat.completions.create(
    model="gpt-4",  # or "gpt-4" if you have access
    messages=[{"role": "user", "content": "talk about wheather"}],
)

print(response.choices[0].message.content)
