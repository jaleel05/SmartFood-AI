import os
import google.generativeai as genai

def load_env():
    """Load API key from .env.local or .env if present"""
    for env_path in ['.env.local', '.env', 'python_backend/.env', '../.env.local']:
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and k not in os.environ:
                            os.environ[k] = v

load_env()

# Get the Gemini API key from environment (.env.local or .env)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY is not set. Please set it in .env.local or .env file.")
    exit(1)

try:
    genai.configure(api_key=GEMINI_API_KEY)
    print("API key configured successfully.")

    # Try to list models to verify the key works
    models = list(genai.list_models())
    print(f"Successfully connected to Gemini API. Found {len(models)} models.")

    # Print available models
    print("\nAvailable models:")
    for model in models[:10]:
        print(f"  - {model.name}")

    # Test generation with gemini-2.5-flash
    model_name = "gemini-2.5-flash"
    print(f"\nTrying to use model: {model_name}")
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hello, this is a test from SmartFood AI!")
    print(f"Test generation successful: {response.text.strip()}")

except Exception as e:
    print(f"Gemini API key test failed: {e}")
    print("The API key may be invalid, expired, or restricted.")
