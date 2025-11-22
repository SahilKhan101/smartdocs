import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env")
    exit(1)

print(f"✓ API Key found: {api_key[:10]}...")

try:
    genai.configure(api_key=api_key)
    print("\n📋 Listing available models:")
    
    models = list(genai.list_models())
    if not models:
        print("❌ No models found! Your API key might be invalid.")
    else:
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                print(f"  ✓ {m.name}")
        
        # Try to use the first available model
        print("\n🧪 Testing first available model...")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Say hello")
        print(f"✓ SUCCESS! Response: {response.text}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPossible issues:")
    print("1. API key is invalid or expired")
    print("2. API key doesn't have Gemini API enabled")
    print("3. You need to enable the Generative Language API in Google Cloud Console")
