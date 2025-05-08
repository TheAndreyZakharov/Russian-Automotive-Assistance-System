# 📂 Parking Dataset

## 🧪 Custom Dataset for Training the Autonomous Parking Model

This folder contains a **handcrafted dataset** collected during manual parking sessions, used to train a model for automatic parking.  
All data was generated from real-time vehicle behavior, sensors, and onboard cameras during various parking attempts.

The dataset includes **camera images** and **telemetry logs**, making it suitable for both visual and sensor-based machine learning models.

### 📁 Dataset Structure

- **`log.csv`**  
  A CSV file containing time-synced vehicle telemetry data with the following parameters:
  - `frame`: Frame number in the sequence  
  - `throttle`: Acceleration input value  
  - `steer`: Steering input value  
  - `brake`: Brake input value  
  - `speed`: Current speed of the vehicle  
  - `front_dist`: Distance to obstacle in front  
  - `back_dist`: Distance to obstacle behind  
  - `left_dist`: Distance to obstacle on the left  
  - `right_dist`: Distance to obstacle on the right  
  
  This file represents the numerical sensor and control data used for model training.

- **`images/`**  
  A folder containing images captured by the vehicle's cameras during each parking session.  
  Each image corresponds to a specific frame in `log.csv`, providing visual context aligned with sensor readings.

This dataset is essential for supervised learning tasks where the system needs to **understand the relationship between sensor readings, visual input, and parking behavior**.

---

<br><br><br><br><br>

---

# 📂 Датасет для парковки

## 🧪 Собственный датасет для обучения модели автоматической парковки

Эта папка содержит **самостоятельно собранный датасет**, использованный для обучения модели, выполняющей автоматическую парковку.  
Данные были собраны в ходе ручной парковки автомобиля с использованием камер и датчиков в разных сценариях.

В датасете присутствуют **изображения с камер** и **телеметрическая информация**, что делает его пригодным как для моделей компьютерного зрения, так и для анализа сенсорных данных.

### 📁 Структура датасета

- **`log.csv`**  
  CSV-файл с телеметрией автомобиля, синхронизированной по времени. Включает следующие параметры:
  - `frame`: Номер кадра в последовательности  
  - `throttle`: Значение акселерации  
  - `steer`: Значение поворота руля  
  - `brake`: Значение торможения  
  - `speed`: Скорость автомобиля  
  - `front_dist`: Расстояние до препятствия спереди  
  - `back_dist`: Расстояние до препятствия сзади  
  - `left_dist`: Расстояние до препятствия слева  
  - `right_dist`: Расстояние до препятствия справа  
  
  Этот файл представляет собой числовые данные управления и сенсоров для обучения модели.

- **`images/`**  
  Папка с изображениями, сделанными камерами автомобиля во время сессий парковки.  
  Каждое изображение связано с конкретным кадром в `log.csv` и даёт визуальный контекст.

Этот датасет играет ключевую роль в задачах обучения с учителем, где необходимо **понять взаимосвязь между сенсорными показаниями, изображениями и поведением автомобиля при парковке**.

---
