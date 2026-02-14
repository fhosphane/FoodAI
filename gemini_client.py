import os
import json
from google import genai


def suggest_recipe(ingredients: list[str]) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing")

    client = genai.Client(api_key=api_key)

    prompt = f"""
Return ONLY valid JSON with keys:
meal_name (string), ingredients (array of strings),
steps (array of strings), notes (string).
Use these ingredients primarily: {ingredients}
"""

    resp = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=prompt,
    )

    # Bazen model JSON'u ```json ... ``` içinde döndürebilir:
    text = resp.text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1].strip()
        if text.startswith("json"):
            text = text[4:].strip()

    return json.loads(text)
