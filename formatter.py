from groq import Groq
import os

FORMATTER_PROMPT = """
You are a data formatting engine.

Your task is to convert attendance records into a clean report format.

Rules:
- Do NOT explain anything.
- Do NOT add commentary.
- Do NOT invent data.
- Do NOT remove records.
- Preserve names, statuses, and timestamps exactly as provided.
- Output must be plain text.
- Use this exact column order:
  Name | Status | Timestamp | Note
- Leave the Note column empty.
- One record per line.
- No markdown.
- No tables.
- No emojis.
- No headings.
- No extra text before or after the output.

If the input is invalid, output exactly:
INVALID_INPUT
"""

def format_attendance(text_input: str) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": FORMATTER_PROMPT},
            {"role": "user", "content": text_input}
        ],
        temperature=0,
        max_tokens=800,
    )

    return completion.choices[0].message.content.strip()
