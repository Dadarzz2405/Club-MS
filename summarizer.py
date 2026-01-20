from groq import Groq
import os

SUMMARIZER_PROMPT = """
You are a meeting minutes summarizer for a school Islamic organization (Rohis).

Your task is to create a VERY brief summary of meeting minutes (notulensi).

Rules:
- Maximum 2-3 sentences only
- Focus on KEY decisions, actions, or topics discussed
- Use simple, clear language
- Do NOT add any commentary or opinions
- Do NOT use markdown or formatting
- Output plain text only
- If the content is too short or unclear, output: "Meeting notes available."

Example input: "Meeting discussed Ramadan program planning. Decided to have iftar together on March 15th. Ahmad will coordinate with cafeteria. Also discussed fundraising ideas for new prayer mats."

Example output: "Discussed Ramadan program planning. Team will organize iftar gathering on March 15th, with Ahmad coordinating logistics. Fundraising ideas proposed for new prayer mats."
"""

def summarize_notulensi(content: str) -> str:
    """
    Summarize notulensi content into 2-3 sentences using AI.
    
    Args:
        content: HTML content from notulensi
        
    Returns:
        Brief summary string (2-3 sentences)
    """
    try:
        # Remove HTML tags for cleaner input
        from html import unescape
        import re
        
        # Strip HTML tags
        clean_text = re.sub('<[^<]+?>', '', content)
        clean_text = unescape(clean_text).strip()
        
        # If content is too short, return as-is
        if len(clean_text) < 50:
            return "Meeting notes available."
        
        # Truncate if too long (to save tokens)
        if len(clean_text) > 2000:
            clean_text = clean_text[:2000] + "..."
        
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SUMMARIZER_PROMPT},
                {"role": "user", "content": clean_text}
            ],
            temperature=0.3,
            max_tokens=150,
        )
        
        summary = completion.choices[0].message.content.strip()
        
        # Fallback if AI returns something weird
        if len(summary) < 10 or len(summary) > 500:
            return "Meeting notes available."
            
        return summary
        
    except Exception as e:
        print(f"Summarization error: {e}")
        return "Meeting notes available."


def get_summary_cache_key(notulensi_id: int) -> str:
    """Generate cache key for notulensi summary"""
    return f"notulensi_summary_{notulensi_id}"