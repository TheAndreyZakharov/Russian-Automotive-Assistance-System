import os
import re
import matplotlib.pyplot as plt

current_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(current_dir, 'train_log.txt')

train_losses = []
val_losses = []
best_epochs = []
epoch_times = []
patience_counts = []

with open(log_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

best_loss = float('inf')
epoch = 0
patience = 0

for line in lines:
    if line.startswith('--- Epoch'):
        epoch += 1

    match = re.search(r'Train Loss: ([0-9.]+) \| Val Loss: ([0-9.]+)', line)
    if match:
        train_losses.append(float(match.group(1)))
        val_losses.append(float(match.group(2)))

    if '[+] New best model saved' in line:
        best_epochs.append(epoch)

    if '[!] No improvement. Patience:' in line:
        patience_counts.append(int(re.search(r'Patience: (\d+)/', line).group(1)))

time_line = [line for line in lines if 'Training finished in' in line]
training_time = time_line[0] if time_line else 'Training time: unknown'

plt.figure(figsize=(12, 7))
plt.plot(train_losses, label='Train Loss', linewidth=2)
plt.plot(val_losses, label='Validation Loss', linewidth=2)

# Отметим все сохранённые модели зелёными звездами, КРОМЕ последней
for i, ep in enumerate(best_epochs[:-1]):
    plt.scatter(ep - 1, val_losses[ep - 1], color='green', marker='*', s=150,
                label='Model Saved' if i == 0 else "")

# Последнюю лучшую модель отметим красной звездой
last_best = best_epochs[-1]
plt.scatter(last_best - 1, val_losses[last_best - 1], color='red', marker='*', s=180, label='Final Best Model')

plt.title('Training & Validation Loss per Epoch')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.grid(True)
plt.legend()

#Добавление текста
plt.text(0.01, 0.98,
         f'Total Epochs: {epoch}\nBest Epoch: {last_best} (Val Loss: {val_losses[last_best - 1]:.4f})\n{training_time.strip()}',
         transform=plt.gca().transAxes,
         fontsize=10,
         verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.tight_layout()
current_dir = os.path.dirname(os.path.abspath(__file__))
plot_path = os.path.join(current_dir, 'training_detailed_plot.png')
plt.savefig(plot_path)
print(f'saved to {plot_path}')
plt.show()
