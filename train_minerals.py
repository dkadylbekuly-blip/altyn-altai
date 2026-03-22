import json
import random
from pathlib import Path

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

from PIL import Image, UnidentifiedImageError
import torch
from torch import nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models

# =========================
# CONFIG
# =========================
DATASET_DIR = Path(r"C:\Users\dkady\OneDrive\Desktop\bazamusei")
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

IMAGE_SIZE = 224
BATCH_SIZE = 16
EPOCHS = 8
LEARNING_RATE = 1e-4
VAL_SPLIT = 0.2
SEED = 42

random.seed(SEED)
torch.manual_seed(SEED)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

if not DATASET_DIR.exists():
    raise FileNotFoundError(f"Dataset folder not found: {DATASET_DIR}")

# =========================
# Проверка и фильтрация файлов
# =========================
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}

def is_valid_image_file(path: str) -> bool:
    p = Path(path)
    if p.suffix.lower() not in VALID_EXTENSIONS:
        return False
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except (UnidentifiedImageError, OSError, ValueError):
        print(f"⚠ Skipped bad image: {path}")
        return False

class_dirs = [p for p in DATASET_DIR.iterdir() if p.is_dir()]
if not class_dirs:
    raise ValueError("No class folders found inside dataset directory.")

print("Classes found:")
for d in class_dirs:
    print(" -", d.name)

# =========================
# TRANSFORMS
# =========================
train_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15),
    transforms.ToTensor(),
])

val_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
])

# =========================
# DATASET
# =========================
full_dataset = datasets.ImageFolder(
    DATASET_DIR,
    transform=train_transform,
    is_valid_file=is_valid_image_file,
    allow_empty=True,
)

class_names = full_dataset.classes
num_classes = len(class_names)

print(f"\nTotal valid images: {len(full_dataset)}")
print(f"Number of classes: {num_classes}")
print("Class names:", class_names)

with open(MODELS_DIR / "classes.json", "w", encoding="utf-8") as f:
    json.dump(class_names, f, ensure_ascii=False, indent=2)

val_size = int(len(full_dataset) * VAL_SPLIT)
train_size = len(full_dataset) - val_size

train_dataset, val_dataset = random_split(
    full_dataset,
    [train_size, val_size],
    generator=torch.Generator().manual_seed(SEED)
)

val_dataset.dataset = datasets.ImageFolder(
    DATASET_DIR,
    transform=val_transform,
    is_valid_file=is_valid_image_file,
    allow_empty=True,
)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

# =========================
# MODEL
# =========================
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
in_features = model.fc.in_features
model.fc = nn.Linear(in_features, num_classes)
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

# =========================
# TRAIN LOOP
# =========================
best_val_acc = 0.0

for epoch in range(EPOCHS):
    model.train()
    train_loss = 0.0
    train_correct = 0
    train_total = 0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        train_loss += loss.item() * images.size(0)
        _, preds = torch.max(outputs, 1)
        train_correct += (preds == labels).sum().item()
        train_total += labels.size(0)

    train_loss /= train_total
    train_acc = train_correct / train_total

    model.eval()
    val_loss = 0.0
    val_correct = 0
    val_total = 0

    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            val_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            val_correct += (preds == labels).sum().item()
            val_total += labels.size(0)

    val_loss /= val_total
    val_acc = val_correct / val_total

    print(
        f"Epoch {epoch+1}/{EPOCHS} | "
        f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
        f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}"
    )

    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save(model.state_dict(), MODELS_DIR / "minerals_best.pth")
        print("✅ Best model saved.")

print("\nTraining finished.")
print(f"Best validation accuracy: {best_val_acc:.4f}")
print(f"Model saved to: {MODELS_DIR / 'minerals_best.pth'}")
print(f"Classes saved to: {MODELS_DIR / 'classes.json'}")