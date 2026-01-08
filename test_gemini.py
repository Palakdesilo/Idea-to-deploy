import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

async def test_model():
    env_path = Path('apps/api/.env')
    load_dotenv(env_path)
    key = os.getenv('GOOGLE_API_KEY') or os.getenv('google_api_key')
    
    if not key:
        print("No key found")
        return

    models = ["gemini-2.0-flash-exp", "gemini-1.5-flash", "models/gemini-1.5-flash", "gemini-pro"]
    
    for m in models:
        try:
            print(f"\nTesting {m}...")
            llm = ChatGoogleGenerativeAI(
                model=m,
                google_api_key=key,
                convert_system_message_to_human=True
            )
            resp = await llm.ainvoke([HumanMessage(content="Hello")])
            print(f"✅ Success with {m}: {resp.content[:20]}...")
            break
        except Exception as e:
            print(f"❌ Failed {m}: {e}")

if __name__ == "__main__":
    asyncio.run(test_model())
