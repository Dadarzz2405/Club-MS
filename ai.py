import os
import re
from groq import Groq

SYSTEM_PROMPT = """
You are an Islamic educational assistant for a school Rohis organization.
Explain concepts clearly and respectfully.
Do not issue fatwas or definitive rulings.
If a question requires a scholar, advise consulting a trusted ustadz.
Give concise short answers focused on Islamic teachings and values.
Avoid using table format.
Avoid using markdown or bold formatting.
If you don't know the answer, say "I'm sorry, I don't have that information."
Do not reference yourself as an AI model.
Keep answers under 200 words.
Do not provide legal, medical, or political advice.

If the user asks to go to a page or feature, respond ONLY with:
NAVIGATE: <page_name>

Valid page names:
dashboard, attendance, members, login
"""

ROUTE_MAP = {
    "dashboard": "/",
    "attendance": "/attendance",
    "members": "/member-list",
    "login": "/login",
}

NAV_REGEX = re.compile(r"^NAVIGATE\s*:\s*(\w+)$", re.IGNORECASE)


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        # Fallback to a placeholder or handle it gracefully if not in autonomous mode
        return None
    return Groq(api_key=api_key)


def call_chatbot_groq(message: str) -> dict:
    if not message or len(message) > 500:
        return {
            "action": "chat",
            "message": "Please ask a shorter question."
        }

    try:
        client = get_groq_client()
        if not client:
             return {
                "action": "chat",
                "message": "Chat service is currently unavailable (API key missing)."
            }

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.strip()},
                {"role": "user", "content": message.strip()}
            ],
            temperature=0.3,
            max_tokens=180,
        )

        content = completion.choices[0].message.content.strip()

        match = NAV_REGEX.match(content)
        if match:
            page = match.group(1).lower()
            route = ROUTE_MAP.get(page)
            if route:
                return {
                    "action": "navigate",
                    "redirect": route
                }

        # --- Normal chat ---
        return {
            "action": "chat",
            "message": content
        }

    except RuntimeError as e:
        print("Config error:", e)
        return {
            "action": "chat",
            "message": "System configuration error."
        }

    except Exception as e:
        print("Groq error:", e)
        return {
            "action": "chat",
            "message": "I'm sorry, I can't respond right now. Please try again later."
        }
