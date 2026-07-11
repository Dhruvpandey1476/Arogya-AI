"""
Fine-tuning script for EfficientNet-B0 on ISIC 2018 Task 3 skin lesion dataset.
Run this BEFORE the hackathon. Requires GPU recommended (Google Colab A100 works well).

Dataset: https://www.kaggle.com/datasets/nodoubttome/skin-cancer9-classesisic
Place images in: backend/data/raw/skin_images/{class_name}/*.jpg

Directory structure expected:
  data/raw/skin_images/
    melanoma/  (or mel/)
    nevus/     (or nv/)
    bcc/
    akiec/
    bkl/
    df/
    vasc/
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms, models, datasets
from pathlib import Path
import json
import sys
import numpy as np
from sklearn.metrics import classification_report

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
import config

DATA_DIR = config.BASE_DIR / "data" / "raw" / "skin_images"
MODEL_OUTPUT = config.SKIN_MODEL_PATH
LABELS_OUTPUT = config.SKIN_LABELS_PATH
EPOCHS = 15
BATCH_SIZE = 32
LR = 1e-4


def get_transforms():
    train_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    val_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    return train_tf, val_tf


def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on: {device}")

    train_tf, val_tf = get_transforms()

    # Load dataset
    full_dataset = datasets.ImageFolder(DATA_DIR, transform=train_tf)
    n = len(full_dataset)
    n_val = int(0.2 * n)
    n_train = n - n_val
    train_set, val_set = torch.utils.data.random_split(full_dataset, [n_train, n_val])
    val_set.dataset.transform = val_tf

    train_loader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_set, batch_size=BATCH_SIZE, shuffle=False, num_workers=4)

    num_classes = len(full_dataset.classes)
    print(f"Classes: {full_dataset.classes}")
    print(f"Train: {len(train_set)}, Val: {len(val_set)}")

    # Save class labels
    MODEL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    labels = {str(i): cls for i, cls in enumerate(full_dataset.classes)}
    with open(LABELS_OUTPUT, "w") as f:
        json.dump(labels, f, indent=2)
    print(f"Labels saved: {LABELS_OUTPUT}")

    # Build model — freeze base, train classifier head first
    model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
    for param in model.parameters():
        param.requires_grad = False
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    model.to(device)

    optimizer = torch.optim.Adam(model.classifier.parameters(), lr=LR)
    criterion = nn.CrossEntropyLoss()
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

    best_val_acc = 0.0

    for epoch in range(EPOCHS):
        # Unfreeze all layers after epoch 5
        if epoch == 5:
            print("Unfreezing all layers for fine-tuning...")
            for param in model.parameters():
                param.requires_grad = True
            optimizer = torch.optim.Adam(model.parameters(), lr=LR * 0.1)

        model.train()
        train_loss, train_correct = 0, 0
        for X, y in train_loader:
            X, y = X.to(device), y.to(device)
            optimizer.zero_grad()
            out = model(X)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            train_correct += (out.argmax(1) == y).sum().item()

        model.eval()
        val_correct, all_preds, all_labels = 0, [], []
        with torch.no_grad():
            for X, y in val_loader:
                X, y = X.to(device), y.to(device)
                out = model(X)
                val_correct += (out.argmax(1) == y).sum().item()
                all_preds.extend(out.argmax(1).cpu().numpy())
                all_labels.extend(y.cpu().numpy())

        train_acc = train_correct / len(train_set)
        val_acc = val_correct / len(val_set)
        scheduler.step()

        print(f"Epoch {epoch+1}/{EPOCHS} | Train Acc: {train_acc:.3f} | Val Acc: {val_acc:.3f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), MODEL_OUTPUT)
            print(f"  ✓ Saved best model (val_acc={best_val_acc:.3f})")

    print(f"\nTraining complete. Best val accuracy: {best_val_acc:.4f}")
    print(f"Model saved to: {MODEL_OUTPUT}")
    print("\nFinal Classification Report:")
    print(classification_report(all_labels, all_preds, target_names=full_dataset.classes))


if __name__ == "__main__":
    train()
