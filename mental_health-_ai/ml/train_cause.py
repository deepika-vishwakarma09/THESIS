
"""
ml/train_cause.py
──────────────────
Fine-tune DistilBERT for CAUSE classification.
 
Run AFTER create_cause_dataset.py:
    python ml/train_cause.py
 
Output:
    ml/saved_models/cause_classifier/
"""
 
import os
import json
import torch
import numpy as np
import pandas as pd
from datetime import datetime
from torch.utils.data import Dataset, DataLoader
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    get_linear_schedule_with_warmup,
)
from torch.optim import AdamW
from sklearn.metrics import classification_report, accuracy_score
 
# ── Config ────────────────────────────────────────────────────────────────────
MODEL_NAME   = "distilbert-base-uncased"
TRAIN_PATH   = "ml/dataset/cause_train.csv"
TEST_PATH    = "ml/dataset/cause_test.csv"
LABEL_PATH   = "ml/dataset/cause_label_map.json"
OUTPUT_DIR   = "ml/saved_models/cause_classifier"
RESULTS_PATH = "ml/saved_models/cause_training_results.json"
 
MAX_LEN       = 128
BATCH_SIZE    = 16
EPOCHS        = 3
LEARNING_RATE = 2e-5
RANDOM_SEED   = 42
 
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
 
 
# ── Dataset ───────────────────────────────────────────────────────────────────
class CauseDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts     = texts
        self.labels    = labels
        self.tokenizer = tokenizer
        self.max_len   = max_len
 
    def __len__(self):
        return len(self.texts)
 
    def __getitem__(self, idx):
        enc = self.tokenizer(
            str(self.texts[idx]),
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids":      enc["input_ids"].squeeze(),
            "attention_mask": enc["attention_mask"].squeeze(),
            "labels":         torch.tensor(self.labels[idx], dtype=torch.long),
        }
 
 
# ── Train epoch ───────────────────────────────────────────────────────────────
def train_epoch(model, loader, optimizer, scheduler):
    model.train()
    total_loss, correct, total = 0, 0, 0
 
    for batch in loader:
        optimizer.zero_grad()
        ids    = batch["input_ids"].to(device)
        mask   = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
 
        out  = model(input_ids=ids, attention_mask=mask, labels=labels)
        loss = out.loss
        loss.backward()
 
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
 
        total_loss += loss.item()
        preds = torch.argmax(out.logits, dim=1)
        correct += (preds == labels).sum().item()
        total   += labels.size(0)
 
    return total_loss / len(loader), correct / total
 
 
# ── Evaluate ──────────────────────────────────────────────────────────────────
def evaluate(model, loader):
    model.eval()
    all_preds, all_labels = [], []
 
    with torch.no_grad():
        for batch in loader:
            ids    = batch["input_ids"].to(device)
            mask   = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            out    = model(input_ids=ids, attention_mask=mask)
            preds  = torch.argmax(out.logits, dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
 
    return accuracy_score(all_labels, all_preds), all_preds, all_labels
 
 
# ── Main ──────────────────────────────────────────────────────────────────────
def train():
    print("=" * 55)
    print("  MindCare AI — Cause Classifier Training")
    print("=" * 55)
    print(f"\n🖥️  Device : {device}")
    print(f"📦 Model  : {MODEL_NAME}")
    print(f"⚙️  Epochs : {EPOCHS} | Batch: {BATCH_SIZE}\n")
 
    # ── Load label map ────────────────────────────────
    with open(LABEL_PATH) as f:
        label_map = json.load(f)
    id2label   = {v: k for k, v in label_map.items()}
    num_labels = len(label_map)
    print(f"🏷️  Causes ({num_labels}):")
    for name, idx in label_map.items():
        print(f"   {idx}: {name}")
 
    # ── Load data ─────────────────────────────────────
    print(f"\n📂 Loading data...")
    train_df = pd.read_csv(TRAIN_PATH)
    test_df  = pd.read_csv(TEST_PATH)
    print(f"   Train: {len(train_df):,} | Test: {len(test_df):,}")
 
    # ── Tokenizer + Datasets ──────────────────────────
    print("\n🔤 Loading tokenizer...")
    tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)
 
    train_ds = CauseDataset(train_df["text"].tolist(), train_df["cause_id"].tolist(), tokenizer, MAX_LEN)
    test_ds  = CauseDataset(test_df["text"].tolist(),  test_df["cause_id"].tolist(),  tokenizer, MAX_LEN)
 
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    test_loader  = DataLoader(test_ds,  batch_size=BATCH_SIZE, shuffle=False)
 
    # ── Model ─────────────────────────────────────────
    print("🧠 Loading DistilBERT for cause classification...")
    model = DistilBertForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=num_labels,
        id2label=id2label,
        label2id=label_map,
    ).to(device)
 
    # ── Optimizer ─────────────────────────────────────
    optimizer   = AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=0.01)
    total_steps = len(train_loader) * EPOCHS
    scheduler   = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=total_steps // 10,
        num_training_steps=total_steps,
    )
 
    # ── Training Loop ─────────────────────────────────
    print("\n" + "─" * 55)
    print("  Training Started...")
    print("─" * 55)
 
    best_acc = 0
    history  = []
 
    for epoch in range(1, EPOCHS + 1):
        print(f"\n📅 Epoch {epoch}/{EPOCHS}")
        train_loss, train_acc = train_epoch(model, train_loader, optimizer, scheduler)
        val_acc, _, _         = evaluate(model, test_loader)
 
        print(f"   Loss     : {train_loss:.4f}")
        print(f"   Train Acc: {train_acc * 100:.2f}%")
        print(f"   Val Acc  : {val_acc * 100:.2f}%")
 
        history.append({
            "epoch":      epoch,
            "train_loss": round(train_loss, 4),
            "train_acc":  round(train_acc, 4),
            "val_acc":    round(val_acc, 4),
        })
 
        if val_acc > best_acc:
            best_acc = val_acc
            print(f"   💾 Best model saved! ({val_acc * 100:.2f}%)")
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            model.save_pretrained(OUTPUT_DIR)
            tokenizer.save_pretrained(OUTPUT_DIR)
 
    # ── Final Report ──────────────────────────────────
    print("\n" + "=" * 55)
    print("  Final Evaluation")
    print("=" * 55)
 
    best_model = DistilBertForSequenceClassification.from_pretrained(OUTPUT_DIR).to(device)
    final_acc, preds, true_labels = evaluate(best_model, test_loader)
    label_names = [id2label[i] for i in range(num_labels)]
    print(f"\n{classification_report(true_labels, preds, target_names=label_names)}")
 
    # ── Save results ──────────────────────────────────
    os.makedirs("ml/saved_models", exist_ok=True)
    results = {
        "model":          MODEL_NAME,
        "num_causes":     num_labels,
        "cause_map":      label_map,
        "best_val_acc":   round(best_acc, 4),
        "final_test_acc": round(final_acc, 4),
        "history":        history,
        "trained_at":     datetime.now().isoformat(),
    }
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
 
    print("=" * 55)
    print(f"  ✅ Cause Model Training Complete!")
    print(f"  🏆 Best Accuracy : {best_acc * 100:.2f}%")
    print(f"  💾 Saved to      : {OUTPUT_DIR}")
    print("=" * 55)
    print("\n🚀 Next: Update ml_service.py → Both models ready!")
 
 
if __name__ == "__main__":
    train()