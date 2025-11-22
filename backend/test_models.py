import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found.")
else:
    print("Testing available models...")
    
    # Try common model names
    models_to_test = [
        "gemini-pro",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.0-pro",
        "models/gemini-pro",
        "models/gemini-1.5-flash"
    ]
    
    for model_name in models_to_test:
        try:
            print(f"\nTrying: {model_name}")
            llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
            response = llm.invoke("Say 'hello'")
            print(f"  ✓ SUCCESS: {model_name} works!")
            print(f"  Response: {response.content}")
            break
        except Exception as e:
            print(f"  ✗ FAILED: {str(e)[:100]}")
