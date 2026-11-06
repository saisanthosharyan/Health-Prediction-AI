import os

import httpx
from dotenv import load_dotenv

load_dotenv()


async def generate_health_remarks(
    age: int,
    glucose: float,
    haemoglobin: float,
    cholesterol: float,
) -> str:
    """
    Generate cautious, informational health observations
    using an external AI API.
    """

    api_key = os.getenv("AI_API_KEY")
    api_url = os.getenv(
        "AI_API_URL",
        "https://openrouter.ai/api/v1/chat/completions",
    )
    model = os.getenv("AI_MODEL", "openai/gpt-4o-mini")

    if not api_key:
        return (
            "AI analysis unavailable: configure AI_API_KEY "
            "to enable external health observations."
        )

    prompt = f"""
    Review these fictional patient blood test values.

    Age: {age}
    Glucose: {glucose} mg/dL
    Haemoglobin: {haemoglobin} g/dL
    Total cholesterol: {cholesterol} mg/dL

    Provide a short, cautious health observation.

    Requirements:
    1. Discuss possible areas that may need medical attention.
    2. Mention possible glucose, haemoglobin or cholesterol concerns
       only where appropriate.
    3. Do not claim to diagnose a disease.
    4. Do not invent missing medical information.
    5. Explain that glucose interpretation depends on fasting status.
    6. Recommend professional medical evaluation when appropriate.
    7. Keep the response under 100 words.
    """

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You provide cautious health information, not "
                    "medical diagnoses. Explain uncertainty clearly."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.2,
        "max_tokens": 180,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                api_url,
                json=payload,
                headers=headers,
            )

            response.raise_for_status()

            result = response.json()

            remarks = (
                result["choices"][0]["message"]["content"].strip()
            )

            if not remarks:
                raise ValueError("The AI API returned an empty response.")

            return remarks

    except (httpx.HTTPError, KeyError, IndexError, ValueError):
        return (
            "AI analysis temporarily unavailable. "
            "Please consult a qualified healthcare professional "
            "for interpretation of these results."
        )