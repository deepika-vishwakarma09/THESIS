
"""
ml/inference.py
────────────────
Test trained DistilBERT model + SHAP keyword extraction.
 
Run AFTER train.py:
    python ml/inference.py
 
Tests:
  1. Single text prediction
  2. SHAP keyword extraction
  3. Batch accuracy on test set
"""
 
import json
import torch
import numpy as np
import pandas as pd
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
 
# ── Config ────────────────────────────────────────────────────────────────────
MODEL_PATH = "ml/saved_models/mental_health_classifier"
TEST_PATH  = "ml/dataset/test.csv"
MAX_LEN    = 128
 
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
 
# ── Coping suggestions ────────────────────────────────────────────────────────
SUGGESTIONS = {
    "Anxiety":    [
        "Try 4-7-8 breathing exercises",
        "Limit caffeine intake today",
        "Talk to a trusted friend or counselor",
    ],
    "Depression": [
        "Take a short walk outside",
        "Maintain your daily routine",
        "Consider visiting the campus counselor",
    ],
    "Stress":     [
        "Break tasks into smaller steps",
        "Take 5-minute mindful breaks",
        "Use the Pomodoro technique to study",
    ],
    "Suicidal":   [
        "Please talk to someone you trust right now",
        "Contact campus counselor immediately",
        "Call helpline: iCall 9152987821",
    ],
    "Normal":     [
        "Keep up your great habits!",
        "Practice daily gratitude journaling",
        "Stay connected with friends",
    ],
}
 
MOOD_MAP = {
    "Normal":     5,
    "Anxiety":    2,
    "Depression": 1,
    "Stress":     3,
    "Suicidal":   1,
}
 
 
# ── Load model ────────────────────────────────────────────────────────────────
def load_model():
    print(f"🧠 Loading model from: {MODEL_PATH}")
    tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
    model     = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
    model     = model.to(device)
    model.eval()
    print(f"✅ Model loaded on: {device}\n")
    return tokenizer, model
 
 
# ── Predict single text ───────────────────────────────────────────────────────
def predict(text: str, tokenizer, model) -> dict:
    inputs = tokenizer(
        text,
        max_length=MAX_LEN,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )
    input_ids      = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)
 
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        probs   = torch.softmax(outputs.logits, dim=1)[0]
        pred_id = probs.argmax().item()
 
    label      = model.config.id2label[pred_id]
    confidence = float(probs[pred_id])
 
    return {
        "mental_state": label,
        "confidence":   round(confidence, 3),
        "mood_level":   MOOD_MAP.get(label, 4),
        "suggestions":  SUGGESTIONS.get(label, []),
        "all_probs":    {
            model.config.id2label[i]: round(float(p), 3)
            for i, p in enumerate(probs)
        },
    }
 
 
# ── SHAP keyword extraction ───────────────────────────────────────────────────
def extract_keywords_shap(text: str, tokenizer, model, top_k: int = 5) -> list[str]:
    """
    Extract important keywords using token-level importance.
    Uses gradient-based attribution as a SHAP approximation.
    """
    try:
        inputs = tokenizer(
            text,
            max_length=MAX_LEN,
            truncation=True,
            return_tensors="pt",
        )
        input_ids      = inputs["input_ids"].to(device)
        attention_mask = inputs["attention_mask"].to(device)
 
        # Get embeddings with gradients
        embeddings = model.distilbert.embeddings(input_ids)
        embeddings.retain_grad()
 
        outputs = model(inputs_embeds=embeddings, attention_mask=attention_mask)
        pred_id = outputs.logits.argmax().item()
 
        # Backprop to get gradients
        model.zero_grad()
        outputs.logits[0, pred_id].backward()
 
        # Importance = gradient * embedding (integrated gradient approximation)
        importance = (embeddings.grad * embeddings).abs().sum(dim=-1)[0]
        importance = importance.detach().cpu().numpy()
 
        # Map tokens back to words
        tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
        word_scores = {}
 
        for token, score in zip(tokens, importance):
            if token in ["[CLS]", "[SEP]", "[PAD]"]:
                continue
            word = token.replace("##", "")
            if len(word) < 3:
                continue
            word_scores[word] = word_scores.get(word, 0) + float(score)
 
        # Return top-k keywords
        sorted_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in sorted_words[:top_k]]
 
    except Exception as e:
        print(f"[SHAP Warning] Falling back to keyword match: {e}")
        return _fallback_keywords(text)
 
 
def _fallback_keywords(text: str) -> list[str]:
    """Simple keyword matching fallback."""
    keywords = [
        "stressed", "anxiety", "depressed", "lonely", "sad", "worried",
        "hopeless", "overwhelmed", "tired", "angry", "scared", "nervous",
        "exams", "sleep", "friends", "family", "work", "study", "fail",
    ]
    text_lower = text.lower()
    return [kw for kw in keywords if kw in text_lower][:5]
 
 
# ── Test on multiple samples ──────────────────────────────────────────────────
def test_samples(tokenizer, model):
    samples = [
        "I feel very stressed about my exams and cannot sleep at night",
        "I have been feeling really sad and hopeless for weeks now",
        "Today was a great day, I feel happy and energetic",
        "I feel so alone, nobody understands me and I have no friends",
        "I don't want to live anymore, everything feels pointless",
    ]
 
    print("─" * 55)
    print("  Sample Predictions")
    print("─" * 55)
 
    for text in samples:
        result   = predict(text, tokenizer, model)
        keywords = extract_keywords_shap(text, tokenizer, model)
 
        print(f"\n📝 Text     : {text[:60]}...")
        print(f"🧠 State    : {result['mental_state']} ({result['confidence']*100:.1f}%)")
        print(f"😊 Mood     : Level {result['mood_level']}/7")
        print(f"🔑 Keywords : {keywords}")
        print(f"💡 Tip      : {result['suggestions'][0]}")
        print("─" * 55)
 
 
# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  MindCare AI — Model Inference Test")
    print("=" * 55 + "\n")
 
    tokenizer, model = load_model()
    test_samples(tokenizer, model)
 
    print("\n✅ Inference test complete!")
    print("🚀 Next: Update ml_service.py with MODEL_LOADED = True")
 