
import os
import sys

prompt_name = "DynamicWireframes"
keyword = "wireframes"
is_in = keyword in prompt_name
print(f"'{keyword}' in '{prompt_name}': {is_in}")

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print("GEMINI_API_KEY is SET")
else:
    print("GEMINI_API_KEY is NOT SET")

try:
    import json
    json.loads("")
except Exception as e:
    print(f"json.loads('') error: {e}")
