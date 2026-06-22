import json 
import os

from openai import OpenAI

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.3-70b-versatile"

def call_json_llm(system:str, user:str)-> dict:
    api_key=os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("API Key is not set. Add it to backend/.env")
    
    client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)

    response=client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role":"system","content":system},
            {"role":"user","content": user},
        ], 
        response_format={"type":"json_object"},
        temperature=0.7,
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("AI returned an empty response")
    
    return json.loads(content)





