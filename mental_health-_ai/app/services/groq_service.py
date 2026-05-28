
import json
from groq import AsyncGroq
from app.config import settings
 
client = AsyncGroq(api_key=settings.GROQ_API_KEY)
 
SYSTEM_PROMPT = """You are a warm, empathetic AI mental health companion for university students 
on the MyUni app. Your role is to:
 
1. Listen carefully and validate the student's feelings
2. Ask gentle, open-ended follow-up questions to understand the root cause
3. Be supportive, non-judgmental, and encouraging
4. Keep responses SHORT — 2 to 3 sentences maximum
5. NEVER diagnose any mental health condition
6. NEVER give medical advice
7. If the student seems in crisis, gently suggest they speak to a counselor
 
Remember: You are a supportive companion, not a therapist."""
 
 
async def get_chat_reply(
    messages: list[dict],
    selected_mood: str | None = None,
) -> str:
    """
    Send conversation history to Groq and get chatbot reply.
 
    Args:
        messages: list of {"role": "user"/"assistant", "content": "..."}
        selected_mood: mood label the user selected (e.g. "Anxious")
 
    Returns:
        Bot reply string
    """
    system = SYSTEM_PROMPT
    if selected_mood:
        system += f"\n\nThe student's self-reported mood right now: {selected_mood}."
 
    try:
        response = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "system", "content": system}, *messages],
            max_tokens=200,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
 
    except Exception as e:
        print(f"[Groq ERROR] {e}")
        return "I'm here for you. Could you tell me a bit more about what's been on your mind?"
 
 
ANALYSIS_SYSTEM_PROMPT = """You are a mental health NLP analysis engine. 
Analyze the conversation and return ONLY valid JSON — no markdown, no extra text.
 
Return this exact structure:
{
  "mental_state": "one of: Anxiety, Depression, Stress, Loneliness, Normal",
  "confidence": 0.85,
  "cause": "e.g. Academic Stress or Social Isolation",
  "keywords": ["word1", "word2", "word3", "word4"],
  "mood_level": 3,
  "summary": "One empathetic sentence about the user's emotional state",
  "suggestions": ["tip1", "tip2", "tip3"]
}"""
 
 
async def analyze_conversation(
    messages: list[dict],
    selected_mood: str | None = None,
    mood_level: int | None = None,
) -> dict:
    """
    Analyze full conversation to extract mental state, cause, keywords.
    Used as a fallback when the DistilBERT model is not yet trained.
    """
    convo_text = "\n".join(
        f"{'User' if m['role'] == 'user' else 'Bot'}: {m['content']}"
        for m in messages
    )
 
    user_prompt = f"""Analyze this conversation from a university student:
 
{convo_text}
 
Self-reported mood: {selected_mood or 'Not specified'} (Level {mood_level or 'unknown'}/7)
 
Return ONLY the JSON object."""
 
    try:
        response = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=400,
            temperature=0.1,
        )
        raw = response.choices[0].message.content.strip()
        # Strip any accidental markdown fences
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
 
    except Exception as e:
        print(f"[Groq Analysis ERROR] {e}")
        # Safe fallback
        return {
            "mental_state": "Stress",
            "confidence": 0.70,
            "cause": "Academic Pressure",
            "keywords": ["stressed", "worried", "overwhelmed"],
            "mood_level": mood_level or 3,
            "summary": "The student appears to be experiencing stress and emotional pressure.",
            "suggestions": [
                "Break tasks into smaller steps",
                "Take short 5-minute mindful breaks",
                "Talk to a friend or campus counselor",
            ],
        }