import json
from io import BytesIO
from pathlib import Path

import torch
from PIL import Image, ImageFile, UnidentifiedImageError
from torchvision import transforms, models
from torch import nn

ImageFile.LOAD_TRUNCATED_IMAGES = True

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "minerals_best.pth"
CLASSES_PATH = BASE_DIR / "models" / "classes.json"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

with open(CLASSES_PATH, "r", encoding="utf-8") as f:
    CLASS_NAMES = json.load(f)

NUM_CLASSES = len(CLASS_NAMES)

model = models.resnet18(weights=None)
in_features = model.fc.in_features
model.fc = nn.Linear(in_features, NUM_CLASSES)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model = model.to(DEVICE)
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])


def predict_image(uploaded_file):
    """
    Принимает UploadedFile из Django и возвращает top-3.
    Если файл не является корректным изображением, выбрасывает ValueError.
    """
    try:
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)

        image = Image.open(BytesIO(file_bytes)).convert("RGB")
        image = transform(image).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            outputs = model(image)
            probs = torch.softmax(outputs, dim=1)[0]

        top_probs, top_idxs = torch.topk(probs, 3)

        results = []
        for prob, idx in zip(top_probs, top_idxs):
            results.append((
                CLASS_NAMES[idx.item()],
                round(prob.item() * 100, 2)
            ))

        return results

    except (UnidentifiedImageError, OSError, ValueError):
        raise ValueError("Не удалось прочитать изображение. Попробуйте другой JPG или PNG файл.")