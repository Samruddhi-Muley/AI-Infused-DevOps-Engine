import json
import os
from groq import Groq
from dotenv import load_dotenv
from utils.prompts import get_diagnosis_prompt

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def diagnose_log(log_text: str) -> dict:
    prompt = get_diagnosis_prompt(log_text)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=500
    )

    raw = response.choices[0].message.content.strip()

    # Clean up any markdown formatting the LLM might add
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    # Find JSON object in response
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    result = json.loads(raw)
    return result