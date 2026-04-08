import google.generativeai as genai
import os
from dotenv import load_dotenv

def test_key():
    load_dotenv()
    # Try to get from .env or ask for input
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        api_key = input("Please enter your Gemini API Key: ")

    if not api_key:
        print("No API Key provided.")
        return

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("Testing connection to Gemini API...")
        response = model.generate_content("Say 'Hello, Gemini is working!'")
        print(f"Response: {response.text}")
        print("\n✅ Success! Your API key is working correctly.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nCommon issues:")
        print("1. Invalid API Key string.")
        print("2. Your region might not be supported (consider using a VPN if in the EU or UK without a billing account).")
        print("3. Billing is not enabled on your Google Cloud project (if using a paid tier).")
        print("4. Network connection issues.")

if __name__ == "__main__":
    test_key()
