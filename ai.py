import os
from groq import Groq

# =========================
# System prompt
# =========================
SYSTEM_PROMPT = """
You are an Islamic educational assistant for a school Rohis organization.
Explain concepts clearly and respectfully.
Do not issue fatwas or definitive rulings.
If a question requires a scholar, advise consulting a trusted ustadz.
Give concise short answers focused on Islamic teachings and values.
Avoid using table format in your responses.
Avoid using '**' for bold text in your responses.
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
    "dashboard": "/dashboard",
    "attendance": "/attendance",
    "members": "/members",
    "login": "/login"
}

# =========================
# Groq client (lazy init)
# =========================
def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")
    return Groq(api_key=api_key)

# =========================
# Main chatbot function
# =========================
def call_chatbot_groq(message: str) -> dict:
    if not message or len(message) > 500:
        return {
            "action": "chat",
            "message": "Please ask a shorter question."
        }

    try:
        client = get_groq_client()

        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.strip()},
                {"role": "user", "content": message}
            ],
            temperature=0.4,
            max_tokens=200,
        )

        content = completion.choices[0].message.content.strip()

        if content.startswith("NAVIGATE:"):
            page = content.replace("NAVIGATE:", "").strip().lower()
            route = ROUTE_MAP.get(page)
            if route:
                return {
                    "action": "navigate",
                    "redirect": route
                }

        return {
            "action": "chat",
            "message": content
        }

    except Exception:
        return {
            "action": "chat",
            "message": "I'm sorry, I can't respond right now. Please try again later."
        }
