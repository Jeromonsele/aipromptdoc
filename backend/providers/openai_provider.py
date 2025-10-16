import os
from typing import Optional, Dict, Any
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

def call_openai(prompt: str, model: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> Optional[str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return None
    client = OpenAI(api_key=api_key)
    model = model or "gpt-4o-mini"
    params = params or {}
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role":"user","content":prompt}],
            temperature=params.get("temperature", 0.2),
        )
        return resp.choices[0].message.content
    except Exception as e:
        return None
