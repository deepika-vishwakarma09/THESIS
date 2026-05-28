
"""
ml/create_cause_dataset.py
───────────────────────────
Creates cause-labeled dataset from existing mental health data.
 
Strategy:
  - Rule-based keyword matching to assign cause labels
  - Each mental state maps to specific causes
  - Creates balanced cause dataset for DistilBERT training
 
Run:
    python ml/create_cause_dataset.py
 
Output:
    ml/dataset/cause_train.csv
    ml/dataset/cause_test.csv
    ml/dataset/cause_label_map.json
"""
 
import pandas as pd
import json
import re
import os
from sklearn.model_selection import train_test_split
 
# ── Config ────────────────────────────────────────────────────────────────────
INPUT_PATH = "ml/dataset/Combined Data.csv"
OUTPUT_DIR = "ml/dataset"
RANDOM_SEED = 42
 
# ── Cause Label Map ───────────────────────────────────────────────────────────
CAUSE_MAP = {
    "Academic Stress":    0,
    "Social Isolation":   1,
    "Family Problems":    2,
    "Relationship Issues":3,
    "Financial Stress":   4,
    "Health Concerns":    5,
    "Work Pressure":      6,
    "Self Worth Issues":  7,
}
 
# ── Keyword Rules — text keywords → cause ────────────────────────────────────
CAUSE_RULES = [
    {
        "cause": "Academic Stress",
        "keywords": [
            "exam", "exams", "study", "studying", "grade", "grades",
            "school", "college", "university", "assignment", "homework",
            "test", "fail", "failing", "teacher", "class", "semester",
            "degree", "thesis", "marks", "result", "tuition", "lecture"
        ]
    },
    {
        "cause": "Social Isolation",
        "keywords": [
            "alone", "lonely", "loneliness", "no friends", "nobody",
            "isolated", "ignored", "left out", "no one", "excluded",
            "friendless", "antisocial", "avoid", "people", "crowd",
            "social", "interaction", "talk", "conversation", "rejected"
        ]
    },
    {
        "cause": "Family Problems",
        "keywords": [
            "family", "parents", "mother", "father", "mom", "dad",
            "brother", "sister", "home", "house", "fight", "argument",
            "abuse", "divorce", "separated", "toxic", "neglect",
            "childhood", "trauma", "domestic", "parent", "relative"
        ]
    },
    {
        "cause": "Relationship Issues",
        "keywords": [
            "breakup", "break up", "boyfriend", "girlfriend", "partner",
            "relationship", "love", "heartbreak", "cheated", "betrayed",
            "trust", "marriage", "divorce", "dating", "rejected",
            "ex", "crush", "affair", "toxic relationship", "abusive"
        ]
    },
    {
        "cause": "Financial Stress",
        "keywords": [
            "money", "financial", "debt", "loan", "poor", "broke",
            "afford", "expensive", "fee", "fees", "rent", "salary",
            "job", "unemployed", "poverty", "income", "bills", "cost",
            "economic", "budget", "spend", "savings", "bank"
        ]
    },
    {
        "cause": "Health Concerns",
        "keywords": [
            "sick", "illness", "disease", "hospital", "doctor",
            "medicine", "pain", "chronic", "disability", "health",
            "body", "weight", "eating", "sleep", "insomnia", "tired",
            "fatigue", "headache", "anxiety attack", "panic attack"
        ]
    },
    {
        "cause": "Work Pressure",
        "keywords": [
            "work", "job", "boss", "office", "colleague", "deadline",
            "overtime", "career", "promotion", "fired", "layoff",
            "workplace", "professional", "business", "pressure",
            "meeting", "project", "manager", "employee", "resign"
        ]
    },
    {
        "cause": "Self Worth Issues",
        "keywords": [
            "worthless", "useless", "failure", "hate myself", "ugly",
            "stupid", "dumb", "incompetent", "hopeless", "burden",
            "self esteem", "confidence", "shame", "guilt", "blame",
            "inferior", "not good enough", "loser", "pathetic", "weak"
        ]
    },
]
 
 
def assign_cause(text: str) -> str | None:
    """
    Assign cause label based on keyword matching.
    Returns cause string or None if no match found.
    """
    text_lower = text.lower()
    scores = {}
 
    for rule in CAUSE_RULES:
        count = sum(1 for kw in rule["keywords"] if kw in text_lower)
        if count > 0:
            scores[rule["cause"]] = count
 
    if not scores:
        return None
 
    # Return cause with highest keyword match count
    return max(scores, key=scores.get)
 
 
def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-z0-9\s.,!?']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
 
 
def create_cause_dataset():
    print("=" * 55)
    print("  MindCare AI — Cause Dataset Creation")
    print("=" * 55)
 
    # ── Load original dataset ──────────────────────────
    print(f"\n📂 Loading dataset: {INPUT_PATH}")
    df = pd.read_csv(INPUT_PATH)
    df = df.rename(columns={"statement": "text", "status": "mental_state"})
    df = df[["text", "mental_state"]]
    print(f"   Total rows: {len(df):,}")
 
    # ── Clean text ────────────────────────────────────
    print("🧹 Cleaning text...")
    df["text"] = df["text"].apply(clean_text)
    df = df[df["text"].str.len() > 10].dropna()
 
    # ── Assign causes ─────────────────────────────────
    print("🏷️  Assigning cause labels via keyword matching...")
    df["cause"] = df["text"].apply(assign_cause)
 
    # Drop rows where no cause found
    before = len(df)
    df = df.dropna(subset=["cause"])
    after = len(df)
    print(f"   Matched: {after:,} / {before:,} rows ({after/before*100:.1f}%)")
 
    # ── Assign cause_id ───────────────────────────────
    df["cause_id"] = df["cause"].map(CAUSE_MAP)
 
    # ── Show distribution ─────────────────────────────
    print("\n📊 Cause Distribution:")
    print(df["cause"].value_counts().to_string())
 
    # ── Balance dataset (max 3000 per cause) ──────────
    print("\n⚖️  Balancing (max 3000 per cause)...")
    df = (
        df.groupby("cause", group_keys=False)
        .apply(lambda x: x.sample(min(len(x), 3000), random_state=RANDOM_SEED))
        .reset_index(drop=True)
    )
    print(f"   Balanced total: {len(df):,}")
 
    # ── Train/Test split ──────────────────────────────
    print("\n✂️  Splitting 80/20...")
    train_df, test_df = train_test_split(
        df[["text", "cause", "cause_id"]],
        test_size=0.2,
        random_state=RANDOM_SEED,
        stratify=df["cause"],
    )
 
    # ── Save ──────────────────────────────────────────
    os.makedirs(OUTPUT_DIR, exist_ok=True)
 
    train_path = os.path.join(OUTPUT_DIR, "cause_train.csv")
    test_path  = os.path.join(OUTPUT_DIR, "cause_test.csv")
    label_path = os.path.join(OUTPUT_DIR, "cause_label_map.json")
 
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path,   index=False)
 
    with open(label_path, "w") as f:
        json.dump(CAUSE_MAP, f, indent=2)
 
    # ── Summary ───────────────────────────────────────
    print("\n" + "=" * 55)
    print("  ✅ Cause Dataset Ready!")
    print("=" * 55)
    print(f"\n📊 Final Stats:")
    print(f"   Train: {len(train_df):,} samples")
    print(f"   Test : {len(test_df):,} samples")
    print(f"   Causes: {len(CAUSE_MAP)} categories")
    print(f"\n📊 Train Cause Distribution:")
    print(train_df["cause"].value_counts().to_string())
    print(f"\n💾 Files saved:")
    print(f"   → {train_path}")
    print(f"   → {test_path}")
    print(f"   → {label_path}")
    print("\n🚀 Next: python ml/train_cause.py")
 
 
if __name__ == "__main__":
    create_cause_dataset()
 