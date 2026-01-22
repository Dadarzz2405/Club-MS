import os
from groq import Groq

FORMATTER_PROMPT = """
You are a data formatting engine.

Your task is to convert attendance records into a clean report format.

Rules:
- Do NOT explain anything.
- Do NOT add commentary.
- Do NOT invent data.
- Do NOT remove records.
- Format timestamps as HH:MM (24-hour format, WIB time) without seconds. Preserve names and statuses exactly as provided.
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


class APIKeyError(Exception):
    """Raised when API key is missing or invalid"""
    pass


def get_groq_client():
    """
    Get Groq client with proper error handling.
    
    Raises:
        APIKeyError: If GROQ_API_KEY is not set in environment
    """
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        raise APIKeyError(
            "GROQ_API_KEY environment variable is not set. "
            "Please set it in your .env file or environment variables."
        )
    
    if not api_key.strip():
        raise APIKeyError(
            "GROQ_API_KEY is empty. Please provide a valid API key."
        )
    
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        raise APIKeyError(f"Failed to initialize Groq client: {str(e)}")


def format_attendance(text_input: str) -> str:
    """
    Format attendance records using AI.
    
    Args:
        text_input: Raw attendance data to format
        
    Returns:
        Formatted attendance string or error message
        
    Raises:
        APIKeyError: If API key is not configured
    """
    if not text_input or not text_input.strip():
        return "INVALID_INPUT"
    
    try:
        client = get_groq_client()
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": FORMATTER_PROMPT},
                {"role": "user", "content": text_input}
            ],
            temperature=0,
            max_tokens=800,
        )

        result = completion.choices[0].message.content.strip()
        
        # Validate result
        if not result:
            return "FORMATTING_ERROR: Empty response from API"
        
        return result
    
    except APIKeyError as e:
        # Re-raise API key errors so they can be handled by caller
        raise
    
    except Exception as e:
        # Log the error and return a user-friendly message
        print(f"Formatting error: {type(e).__name__}: {e}")
        return f"FORMATTING_ERROR: {str(e)}"