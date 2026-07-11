import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import json
import numpy as np
from pathlib import Path
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# Default ISIC 2018 Task 3 class labels
DEFAULT_LABELS = {
    "0": "Melanoma",
    "1": "Melanocytic Nevi",
    "2": "Basal Cell Carcinoma",
    "3": "Actinic Keratosis",
    "4": "Benign Keratosis",
    "5": "Dermatofibroma",
    "6": "Vascular Lesions",
}

# Risk level mapping
RISK_LEVELS = {
    "Melanoma": "concerning",
    "Melanocytic Nevi": "monitor",
    "Basal Cell Carcinoma": "concerning",
    "Actinic Keratosis": "monitor",
    "Benign Keratosis": "benign",
    "Dermatofibroma": "benign",
    "Vascular Lesions": "monitor",
}

# Image preprocessing for EfficientNet
TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


class SkinClassifier:
    def __init__(self, model_path: Path, labels_path: Path):
        # Load class labels
        if labels_path.exists():
            with open(labels_path) as f:
                self.labels = json.load(f)
        else:
            self.labels = DEFAULT_LABELS
            logger.warning("Using default ISIC labels")

        num_classes = len(self.labels)

        # Build EfficientNet-B0
        self.model = models.efficientnet_b0(weights=None)
        self.model.classifier[1] = nn.Linear(
            self.model.classifier[1].in_features, num_classes
        )

        # Load weights
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        state_dict = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()

        logger.info(f"Skin classifier loaded. Device: {self.device}, Classes: {num_classes}")

    def predict(self, image: Image.Image) -> Dict:
        """Predict skin condition from PIL Image."""
        tensor = TRANSFORM(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(tensor)
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]

        top_idx = int(np.argmax(probs))
        condition = self.labels.get(str(top_idx), f"Class {top_idx}")
        confidence = round(float(probs[top_idx]) * 100, 1)
        risk_level = RISK_LEVELS.get(condition, "monitor")

        return {
            "condition": condition,
            "confidence": confidence,
            "risk_level": risk_level,
        }
