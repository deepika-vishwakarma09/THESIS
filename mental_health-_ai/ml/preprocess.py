

"""
ml/preprocess.py
─────────────────
Dataset cleaning + preprocessing for DistilBERT training.
 
Run this first:
    python ml/preprocess.py
 
Output:
    ml/dataset/train.csv
    ml/dataset/test.csv
    ml/dataset/label_map.json
"""
 
import pandas as pd
import json
import re
import os
from sklearn.model_selection import train_test_split
 
# ── Config ────────────────────────────────────────────────────────────────────
INPUT_PATH  = "ml/dataset/Combined Data.csv"
OUTPUT_DIR  = "ml/dataset"
RANDOM_SEED = 42
 
# ── Labels we want to keep ────────────────────────────────────────────────────
KEEP_LABELS = ["Anxiety", "Depression", "Stress", "Normal", "Suicidal"]
 
# ── Label → integer mapping ───────────────────────────────────────────────────
LABEL_MAP = {
    "Normal":     0,
    "Anxiety":    1,
    "Depression": 2,
    "Stress":     3,
    "Suicidal":   4,
}
 
 
def clean_text(text: str) -> str:
    """Basic text cleaning for NLP."""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r"http\S+|www\S+", "", text)       # remove URLs
    text = re.sub(r"[^a-z0-9\s.,!?']", " ", text)   # keep basic punctuation
    text = re.sub(r"\s+", " ", text).strip()          # collapse spaces
    return text
 
 
def preprocess():
    print("=" * 50)
    print("  MindCare AI — Dataset Preprocessing")
    print("=" * 50)
 
    # ── Load ──────────────────────────────────────────
    print(f"\n📂 Loading dataset from: {INPUT_PATH}")
    df = pd.read_csv(INPUT_PATH)
    print(f"   Total rows loaded: {len(df):,}")
 
    # ── Rename columns ────────────────────────────────
    df = df.rename(columns={"statement": "text", "status": "label"})
    df = df[["text", "label"]]
 
    # ── Filter labels ─────────────────────────────────
    print(f"\n🏷️  Filtering to keep: {KEEP_LABELS}")
    df = df[df["label"].isin(KEEP_LABELS)].copy()
    print(f"   Rows after filtering: {len(df):,}")
 
    # ── Drop nulls ────────────────────────────────────
    df = df.dropna(subset=["text", "label"])
    df = df[df["text"].str.strip() != ""]
 
    # ── Clean text ────────────────────────────────────
    print("\n🧹 Cleaning text...")
    df["text"] = df["text"].apply(clean_text)
    df = df[df["text"].str.len() > 10]  # remove too-short texts
 
    # ── Map labels to integers ────────────────────────
    df["label_id"] = df["label"].map(LABEL_MAP)
 
    # ── Balance dataset (max 5000 per class) ──────────
    print("\n⚖️  Balancing dataset (max 5000 per class)...")
    df = (
        df.groupby("label", group_keys=False)
        .apply(lambda x: x.sample(min(len(x), 5000), random_state=RANDOM_SEED))
        .reset_index(drop=True)
    )
 
    # ── Train / Test split (80/20) ────────────────────
    print("\n✂️  Splitting into train (80%) and test (20%)...")
    train_df, test_df = train_test_split(
        df, test_size=0.2, random_state=RANDOM_SEED, stratify=df["label"]
    )
 
    # ── Save ──────────────────────────────────────────
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    train_path = os.path.join(OUTPUT_DIR, "train.csv")
    test_path  = os.path.join(OUTPUT_DIR, "test.csv")
    label_path = os.path.join(OUTPUT_DIR, "label_map.json")
 
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path,   index=False)
 
    with open(label_path, "w") as f:
        json.dump(LABEL_MAP, f, indent=2)
 
    # ── Summary ───────────────────────────────────────
    print("\n" + "=" * 50)
    print("  ✅ Preprocessing Complete!")
    print("=" * 50)
    print(f"\n📊 Final Dataset Stats:")
    print(f"   Train samples : {len(train_df):,}")
    print(f"   Test samples  : {len(test_df):,}")
    print(f"\n📊 Train Label Distribution:")
    print(train_df["label"].value_counts().to_string())
    print(f"\n💾 Files saved:")
    print(f"   → {train_path}")
    print(f"   → {test_path}")
    print(f"   → {label_path}")
    print("\n🚀 Next step: python ml/train.py")
 
 
if __name__ == "__main__":
    preprocess()