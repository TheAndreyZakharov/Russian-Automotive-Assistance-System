import os
import csv
import cv2
import glob
import torch
import numpy as np
import time
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader, random_split
from torch import nn, optim
from torchvision import transforms, models
from torch.optim.lr_scheduler import CosineAnnealingLR

# === Конфигурация ===
IMAGE_DIR = 'C:/images'
CSV_FILE = 'dataset/log.csv'
MODEL_DIR = 'models'
BATCH_SIZE = 8
EPOCHS = 100
LEARNING_RATE = 1e-4
IMG_WIDTH = 320
IMG_HEIGHT = 240
VAL_SPLIT = 0.2
PATIENCE = 10
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
NUM_WORKERS = os.cpu_count() // 2

transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((IMG_HEIGHT+20, IMG_WIDTH+20)),
    transforms.RandomCrop((IMG_HEIGHT, IMG_WIDTH)),
    transforms.ColorJitter(0.2, 0.2, 0.2, 0.1),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor()
])

normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

class ParkingDataset(Dataset):
    def __init__(self, csv_path, img_dir):
        self.img_dir = img_dir
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            self.data = [row for row in reader if row[0].isdigit()]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        frame, throttle, steer, brake = int(self.data[idx][0]), float(self.data[idx][1]), float(self.data[idx][2]), float(self.data[idx][3])
        radar = torch.tensor(list(map(float, self.data[idx][5:9])), dtype=torch.float32)
        imgs = []
        for cam in ['front', 'back', 'left', 'right']:
            path = os.path.join(self.img_dir, f'{cam}_{frame:05d}.png')
            img = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
            img = transform(img)
            img = normalize(img)
            imgs.append(img)

        img_tensor = torch.cat(imgs, dim=0)
        output_tensor = torch.tensor([throttle, steer, brake], dtype=torch.float32)
        return img_tensor, radar, output_tensor

class MultiCamNet(nn.Module):
    def __init__(self):
        super().__init__()
        backbone = models.resnet34(pretrained=True)
        self.cnn = nn.Sequential(*list(backbone.children())[:-1])
        cnn_out_dim = 512 * 4

        self.fc = nn.Sequential(
            nn.Linear(cnn_out_dim + 4, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 3)
        )

    def forward(self, img, radar):
        imgs = torch.split(img, 3, dim=1)
        cnn_out = [self.cnn(i).view(img.size(0), -1) for i in imgs]
        cnn_out = torch.cat(cnn_out, dim=1)
        x = torch.cat([cnn_out, radar], dim=1)
        return self.fc(x)

def train():
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("Using CPU")

    start_time = time.time()
    dataset = ParkingDataset(CSV_FILE, IMAGE_DIR)
    val_size = int(len(dataset) * VAL_SPLIT)
    train_ds, val_ds = random_split(dataset, [len(dataset)-val_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS, pin_memory=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, num_workers=NUM_WORKERS, pin_memory=True)

    model = MultiCamNet().to(DEVICE)
    criterion = nn.SmoothL1Loss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = CosineAnnealingLR(optimizer, T_max=EPOCHS)

    best_val_loss = float('inf')
    patience_counter = 0
    train_losses, val_losses = [], []

    for epoch in range(EPOCHS):
        print(f"\n--- Epoch {epoch + 1}/{EPOCHS} ---")
        model.train()
        total_train_loss = 0
        for imgs, radar, targets in train_loader:
            imgs, radar, targets = imgs.to(DEVICE), radar.to(DEVICE), targets.to(DEVICE)
            optimizer.zero_grad()
            preds = model(imgs, radar)
            loss = criterion(preds, targets)
            loss.backward()
            optimizer.step()
            total_train_loss += loss.item()

        model.eval()
        total_val_loss = 0
        with torch.no_grad():
            for imgs, radar, targets in val_loader:
                imgs, radar, targets = imgs.to(DEVICE), radar.to(DEVICE), targets.to(DEVICE)
                preds = model(imgs, radar)
                total_val_loss += criterion(preds, targets).item()

        avg_train = total_train_loss / len(train_loader)
        avg_val = total_val_loss / len(val_loader)
        train_losses.append(avg_train)
        val_losses.append(avg_val)
        scheduler.step()

        print(f"Train Loss: {avg_train:.4f} | Val Loss: {avg_val:.4f}")

        if avg_val < best_val_loss:
            best_val_loss = avg_val
            patience_counter = 0
            torch.save(model.state_dict(), os.path.join(MODEL_DIR, 'best_model.pth'))
            print("[+] New best model saved")
        else:
            patience_counter += 1
            print(f"[!] No improvement. Patience: {patience_counter}/{PATIENCE}")
            if patience_counter >= PATIENCE:
                print("[!] Early stopping triggered.")
                break

    elapsed = (time.time() - start_time) / 60
    print(f"\n[*] Training finished in {elapsed:.2f} minutes.")

    plt.plot(train_losses, label='Train Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.legend()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, 'plot_results')
    os.makedirs(output_dir, exist_ok=True)

    plt.savefig(os.path.join(output_dir, 'loss_plot.png'))

if __name__ == '__main__':
    os.makedirs(MODEL_DIR, exist_ok=True)
    train()
