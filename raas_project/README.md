# 🚗 Russian Automotive Assistance System (RAAS)

## 🧠 Intelligent Driver Assistance and Vehicle Control Platform

This is the **main directory** of the RAAS project — an integrated system designed to assist drivers with automation, safety, and situational awareness using sensors, cameras, and AI-based modules.

The project is organized into multiple components that handle **vehicle control, environment simulation, driver assistance features, multimedia, and model training**.  
It is built to work in coordination with the **CARLA simulator**, providing a realistic testing ground for autonomous features.

---

### 📁 Folder Overview

- **`main_func/`**  
  Contains core vehicle functionality modules such as camera perspectives, vehicle control, and mirror systems.  
  These are essential for direct vehicle interaction and perception.  

- **`raas_func/`**  
  Implements the intelligent driver assistance features, including emergency braking, lane assist, fatigue detection, multimedia systems, and more.  
  This is the brain of the RAAS system.  

- **`static/`**  
  Stores all multimedia assets such as photos, videos, and GIFs used in the system interface.  
  Also includes unused or archived media resources.  

- **`world_setup/`**  
  Contains tools for creating and managing the simulation world: vehicle spawning, traffic generation, data recording, etc.  
  Used to replicate real-world conditions in CARLA.  

---

### 🖥️ Launcher Files

- **`launch_carla_sync.bat`**  
  Launches the CARLA simulator in synchronized mode with predefined settings.

- **`start_raas.bat`**  
  Sequentially launches the main components of RAAS:  
  vehicle spawning, camera view, control systems, and the multimedia panel — simulating a full runtime environment.

These batch files serve as a **quick-start mechanism**, simplifying the process of launching the RAAS system for testing or development.

---

This root folder ties the system together, acting as the **entry point for all modules**. It enables smooth coordination between simulation, automation, and user interface layers of the driver assistance platform.

---

<br><br><br><br><br>

---

# 🚗 Russian Automotive Assistance System (RAAS)

## 🧠 Интеллектуальная система помощи водителю и управления автомобилем

Это **главная директория** проекта RAAS — комплексной системы, разработанной для помощи водителю с помощью автоматизации, функций безопасности и восприятия обстановки с использованием камер, сенсоров и ИИ-модулей.

Проект структурирован по компонентам, реализующим **управление автомобилем, симуляцию окружения, интеллектуальные функции помощи, мультимедийные модули и обучение моделей**.  
Система работает совместно с **симулятором CARLA**, обеспечивая реалистичную платформу для тестирования.

---

### 📁 Обзор папок

- **`main_func/`**  
  Содержит модули основной функциональности автомобиля — управление, камеры, зеркала.  
  Это базовые инструменты взаимодействия с транспортом.  

- **`raas_func/`**  
  Реализует интеллектуальные функции помощи водителю: экстренное торможение, удержание в полосе, контроль усталости, мультимедиа и др.  
  Это — мозг всей системы RAAS.  

- **`static/`**  
  Содержит все мультимедийные ресурсы: фото, гифки, видео, используемые в интерфейсе.  
  Также включает неиспользованные или архивные материалы.  

- **`world_setup/`**  
  Включает инструменты создания и управления симуляцией: спавн машин, генерация трафика, запись данных и прочее.  
  Используется для воссоздания дорожной среды в CARLA.  

---

### 🖥️ Файлы запуска

- **`launch_carla_sync.bat`**  
  Запускает симулятор CARLA в синхронном режиме с нужными параметрами.

- **`start_raas.bat`**  
  Последовательно запускает основные компоненты системы RAAS:  
  создание автомобиля, камеры, управление, мультимедиа — для полной симуляции работы системы.

Эти `.bat` файлы служат **удобным способом запуска системы**, упрощая тестирование и разработку.

---

Эта корневая папка объединяет все модули и является **точкой входа в систему**. Она обеспечивает слаженную работу симуляции, автоматики и пользовательского интерфейса в рамках RAAS.

---
