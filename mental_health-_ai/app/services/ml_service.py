"""
app/services/ml_service.py
───────────────────────────
Real DistilBERT inference — Mental State + Cause detection + SHAP keywords.
 
7 Mood Scale:
  1 = Angry    → Suicidal
  2 = Anxious  → Anxiety
  3 = Tired    → Depression
  4 = Okay     → Stress
  5 = Joyful   → (user selected / mild normal)
  6 = Happy    → Normal
  7 = Excited  → (user selected / very positive)
"""
 
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
 
# ── Model Paths ───────────────────────────────────────────────────────────────
MENTAL_MODEL_PATH = "ml/saved_models/mental_health_classifier"
CAUSE_MODEL_PATH  = "ml/saved_models/cause_classifier"
MAX_LEN           = 128
 
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
 
# ── 7 Mood Scale Mapping ──────────────────────────────────────────────────────
# AI prediction → mood level (1 to 7)
#
# Level 1 = Angry    → worst mental state (Suicidal)
# Level 2 = Anxious  → Anxiety
# Level 3 = Tired    → Depression
# Level 4 = Okay     → Stress
# Level 5 = Joyful   → mild Normal (slightly better)
# Level 6 = Happy    → Normal (good state)
# Level 7 = Excited  → user selected only (very positive)
#
MOOD_MAP = {
    "Suicidal":   1,   # 😡 Angry   — critical state
    "Anxiety":    2,   # 😰 Anxious — high concern
    "Depression": 3,   # 😴 Tired   — low mood
    "Stress":     4,   # 😐 Okay    — manageable
    "Normal":     6,   # 😄 Happy   — good state
}
 
# ── Coping Suggestions ────────────────────────────────────────────────────────
COPING_TIPS = {
    "Anxiety": [
        "Try 4-7-8 breathing exercises",
        "Limit caffeine intake today",
        "Talk to a trusted friend or counselor",
    ],
    "Depression": [
        "Take a short walk outside",
        "Maintain your daily routine",
        "Consider visiting the campus counselor",
    ],
    "Stress": [
        "Break tasks into smaller steps",
        "Take 5-minute mindful breaks",
        "Use the Pomodoro technique to study",
    ],
    "Suicidal": [
        "Please talk to someone you trust right now",
        "Contact campus counselor immediately",
        "Call helpline: iCall 9152987821",
    ],
    "Normal": [
        "Keep up your great habits!",
        "Practice daily gratitude journaling",
        "Stay connected with friends",
    ],
}
 
# ── Load Mental State Model ───────────────────────────────────────────────────
print(f"\n🧠 Loading Mental State model from: {MENTAL_MODEL_PATH}")
mental_tokenizer = DistilBertTokenizerFast.from_pretrained(MENTAL_MODEL_PATH)
mental_model     = DistilBertForSequenceClassification.from_pretrained(MENTAL_MODEL_PATH)
mental_model     = mental_model.to(device)
mental_model.eval()
print("✅ Mental State model loaded!")
 
# ── Load Cause Model ──────────────────────────────────────────────────────────
print(f"🧠 Loading Cause model from: {CAUSE_MODEL_PATH}")
cause_tokenizer = DistilBertTokenizerFast.from_pretrained(CAUSE_MODEL_PATH)
cause_model     = DistilBertForSequenceClassification.from_pretrained(CAUSE_MODEL_PATH)
cause_model     = cause_model.to(device)
cause_model.eval()
print("✅ Cause model loaded!\n")
 
MODEL_LOADED = True
 
 
# ── Mental State Prediction ───────────────────────────────────────────────────
def predict_mental_state(text: str) -> dict:
    """
    Predict mental state using fine-tuned DistilBERT.
 
    Input : any text (chat conversation)
    Output: mental_state, confidence, mood_level (1-7), suggestions
    """
    inputs = mental_tokenizer(
        text,
        max_length=MAX_LEN,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )
    input_ids      = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)
 
    with torch.no_grad():
        outputs = mental_model(input_ids=input_ids, attention_mask=attention_mask)
        probs   = torch.softmax(outputs.logits, dim=1)[0]
        pred_id = probs.argmax().item()
 
    label      = mental_model.config.id2label[pred_id]
    confidence = float(probs[pred_id])
    mood_level = MOOD_MAP.get(label, 4)
 
    return {
        "mental_state": label,
        "confidence":   round(confidence, 3),
        "mood_level":   mood_level,
        "suggestions":  COPING_TIPS.get(label, []),
    }
 
 
# ── Cause Prediction ──────────────────────────────────────────────────────────
def predict_cause(text: str) -> dict:
    """
    Predict cause of mental state using fine-tuned DistilBERT cause classifier.
 
    Input : any text (chat conversation)
    Output: cause (e.g. Academic Stress), cause_confidence
    """
    inputs = cause_tokenizer(
        text,
        max_length=MAX_LEN,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )
    input_ids      = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)
 
    with torch.no_grad():
        outputs = cause_model(input_ids=input_ids, attention_mask=attention_mask)
        probs   = torch.softmax(outputs.logits, dim=1)[0]
        pred_id = probs.argmax().item()
 
    cause      = cause_model.config.id2label[pred_id]
    confidence = float(probs[pred_id])
 
    return {
        "cause":            cause,
        "cause_confidence": round(confidence, 3),
    }
 
 
# ── SHAP Keyword Extraction ───────────────────────────────────────────────────
def extract_keywords_shap(text: str, mental_state: str, top_k: int = 5) -> list[str]:
    """
    Extract important keywords using gradient-based attribution.
    This is the XAI (Explainable AI) part of the thesis.
 
    Uses integrated gradients as SHAP approximation — shows WHICH
    words caused the model to predict a certain mental state.
    """
    try:
        inputs = mental_tokenizer(
            text,
            max_length=MAX_LEN,
            truncation=True,
            return_tensors="pt",
        )
        input_ids      = inputs["input_ids"].to(device)
        attention_mask = inputs["attention_mask"].to(device)
 
        # Get word embeddings (with grad tracking)
        embeddings = mental_model.distilbert.embeddings(input_ids)
        embeddings.retain_grad()
 
        # Forward pass
        outputs = mental_model(inputs_embeds=embeddings, attention_mask=attention_mask)
        pred_id = outputs.logits.argmax().item()
 
        # Backward pass — get gradients
        mental_model.zero_grad()
        outputs.logits[0, pred_id].backward()
 
        # Importance score = gradient × embedding value
        importance = (embeddings.grad * embeddings).abs().sum(dim=-1)[0]
        importance = importance.detach().cpu().numpy()
 
        # Map tokens → words with scores
        tokens      = mental_tokenizer.convert_ids_to_tokens(input_ids[0])
        word_scores = {}
 
        for token, score in zip(tokens, importance):
            if token in ["[CLS]", "[SEP]", "[PAD]"]:
                continue
            word = token.replace("##", "")   # merge subword tokens
            if len(word) < 3:
                continue
            word_scores[word] = word_scores.get(word, 0) + float(score)
 
        # Return top-k most important words
        sorted_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in sorted_words[:top_k]]
 
    except Exception as e:
        print(f"[SHAP Warning] Using fallback: {e}")
        return _fallback_keywords(text, mental_state)
 
 
def _fallback_keywords(text: str, mental_state: str) -> list[str]:
    """Simple keyword matching fallback if SHAP fails."""
    KEYWORD_POOL = {
        "Anxiety":    ["anxious", "worried", "panic", "nervous", "exams", "fear", "scared"],
        "Depression": ["sad", "hopeless", "empty", "tired", "unmotivated", "worthless"],
        "Stress":     ["stressed", "overwhelmed", "deadline", "pressure", "busy", "exhausted"],
        "Suicidal":   ["end", "die", "hopeless", "worthless", "pointless", "cant go on"],
        "Normal":     ["good", "okay", "happy", "fine", "better", "great"],
    }
    pool       = KEYWORD_POOL.get(mental_state, [])
    text_lower = text.lower()
    found      = [kw for kw in pool if kw in text_lower]
    return (found + pool)[:5]
 
 
# ── MAIN FUNCTION — Both Models Together ─────────────────────────────────────
def full_predict(text: str) -> dict:
    """
    Run BOTH models and return complete analysis.
 
    Called from: app/routers/analyze.py
 
    Returns:
        mental_state     : "Anxiety" / "Depression" / "Stress" / "Suicidal" / "Normal"
        confidence       : 0.0 – 1.0  (Mental State confidence)
        mood_level       : 1 – 7      (mapped to 7-mood scale)
        suggestions      : list of 3 coping tips
        cause            : "Academic Stress" / "Social Isolation" / etc.
        cause_confidence : 0.0 – 1.0  (Cause confidence)
        keywords         : list of important words (SHAP explainability)
    """
    mental_result = predict_mental_state(text)
    cause_result  = predict_cause(text)
    keywords      = extract_keywords_shap(text, mental_result["mental_state"])
 
    return {
        "mental_state":      mental_result["mental_state"],
        "confidence":        mental_result["confidence"],
        "mood_level":        mental_result["mood_level"],
        "suggestions":       mental_result["suggestions"],
        "cause":             cause_result["cause"],
        "cause_confidence":  cause_result["cause_confidence"],
        "keywords":          keywords,
    }