try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("SUCCESS")
except ImportError as e:
    print(f"FAILED: {e}")
