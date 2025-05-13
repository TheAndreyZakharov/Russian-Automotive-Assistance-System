<p align="center">
  <img src="raas_project/static/media/RAAS_logo_rounded.png" alt="RAAS Logo" width="300"/><br><br>
  <a href="https://github.com/TheAndreyZakharov/Russian-Automotive-Assistance-System/blob/main/README.md">
    <img src="https://img.shields.io/badge/README-English-brightgreen">
  </a>
  <a href="https://github.com/TheAndreyZakharov/Russian-Automotive-Assistance-System/blob/main/README_RU.md">
    <img src="https://img.shields.io/badge/README-Русский-blue">
  </a>
</p>

<br>

---

**Russian Automotive Assistance System (RAAS)** is a modular driver assistance system developed based on the CARLA simulator.  
The system is designed as a concept and prototype demonstrating **how such technologies can be implemented for domestic vehicles**, such as Lada, Aurus, and others.

RAAS includes a wide range of ADAS (Advanced Driver Assistance Systems) features, such as automatic parking, blind spot monitoring, emergency braking, lane keeping, 360° cameras, fatigue monitoring, and much more.

The goal of the project is to **propose an architecture, approach, and technical solution** that can be adapted for modern Russian vehicles.  
This is my personal engineering vision of **what a domestically developed driver assistance system could look like** — open, modular, and suitable for real-world use.

In this file, you will find the **complete project structure**, detailed descriptions of how each module works, the architecture of component interaction, as well as **visual examples** of the system in action.  
The `README` serves as the central entry point into the project — for getting acquainted, launching, testing individual features, and understanding how the system is structured and functions as a whole.

❗️ In addition to this description, it is also recommended to review the materials in the [`docs`](docs/) folder, which include explanatory notes, systems analysis, modeling, and rationale for design decisions.  
These documents will help better understand the **goals of the project, its focus, relevance, and the technical context** in which the system was developed.  
For those interested not only in implementation but also in the logic behind RAAS architecture, exploring the contents of `docs` will be especially useful.

---

<br><br><br><br><br>

---

# 📚 Table of Contents

---

- [📚 Table of Contents](#-table-of-contents)
    - [❗️ Important Notes for System Operation:](#️-important-notes-for-system-operation)
    - [📑 Additional README Files](#-additional-readme-files)
    - [📌 Attention When Reading Documentation](#-attention-when-reading-documentation)
    - [❗️ Media File Loading Delay](#️-media-file-loading-delay)
- [🛜 RAAS Modules (raas\_func)](#-raas-modules-raas_func)
  - [🚘 Logic and Functions of the Intelligent Driver Assistance Platform](#-logic-and-functions-of-the-intelligent-driver-assistance-platform)
    - [📁 Folder Contents](#-folder-contents)
    - [📜 Script Descriptions](#-script-descriptions)
    - [🎛️ RAAS Multimedia Panel (`multimedia_panel.py`)](#️-raas-multimedia-panel-multimedia_panelpy)
      - [▶️ Launch Command](#️-launch-command)
      - [🖥️ Example Console Output](#️-example-console-output)
      - [📜 More About Script Operation](#-more-about-script-operation)
    - [🛣️ Lane Keeping Assist System (`lane_keeping_assist.py`)](#️-lane-keeping-assist-system-lane_keeping_assistpy)
      - [📜 More About Script Operation](#-more-about-script-operation-1)
    - [⚠️ Blind Spot Monitoring System (`mirror_alert_toggle.py`)](#️-blind-spot-monitoring-system-mirror_alert_togglepy)
      - [📜 More About Script Operation](#-more-about-script-operation-2)
    - [🧿 360-Degree Camera View (`camera_360_view.py`)](#-360-degree-camera-view-camera_360_viewpy)
      - [📜 More About Script Operation](#-more-about-script-operation-3)
    - [🛑 Emergency Braking System (`emergency_braking.py`)](#-emergency-braking-system-emergency_brakingpy)
      - [📜 More About Script Operation](#-more-about-script-operation-4)
    - [🚨 Automatic Emergency Call System (`emergency_call_monitor.py`)](#-automatic-emergency-call-system-emergency_call_monitorpy)
      - [📜 More About Script Operation](#-more-about-script-operation-5)
    - [🛣️ Adaptive Cruise Control (`adaptive_cruise_control.py`)](#️-adaptive-cruise-control-adaptive_cruise_controlpy)
      - [📜 More About Script Operation](#-more-about-script-operation-6)
    - [🛣️ Driver Fatigue Monitoring (`driver_fatigue_monitor.py`)](#️-driver-fatigue-monitoring-driver_fatigue_monitorpy)
      - [📜 More About Script Operation](#-more-about-script-operation-7)
    - [🎥 Emergency Camera Recording (`camera_recorder.py`)](#-emergency-camera-recording-camera_recorderpy)
      - [📜 More About Script Operation](#-more-about-script-operation-8)
    - [🅿️ Test Functionality: Smart Parking (`smart_parking.py`)](#️-test-functionality-smart-parking-smart_parkingpy)
      - [📜 More About Script Operation](#-more-about-script-operation-9)
    - [🗃️ Working with the Database (`database_logger.py`)](#️-working-with-the-database-database_loggerpy)
      - [📜 More About Script Operation](#-more-about-script-operation-10)
    - [🗂️ Smart Parking (`smart_parking_train`)](#️-smart-parking-smart_parking_train)
      - [🚗 Autonomous Vehicle Parking Using a Custom Dataset and Neural Network](#-autonomous-vehicle-parking-using-a-custom-dataset-and-neural-network)
    - [📁 Folder Contents](#-folder-contents-1)
    - [📊 Training Results Visualization and Analysis (`plot_training.py`)](#-training-results-visualization-and-analysis-plot_trainingpy)
      - [📜 More About Script Operation](#-more-about-script-operation-11)
    - [🎥 Custom Dataset Recording (`record_data.py`)](#-custom-dataset-recording-record_datapy)
      - [📜 More About Script Operation](#-more-about-script-operation-12)
    - [🧠 Training the Smart Parking Model (`train_model.py`)](#-training-the-smart-parking-model-train_modelpy)
      - [📜 More About Script Operation](#-more-about-script-operation-13)
    - [🤖 Smart Parking Model Testing (`smart_parking.py`)](#-smart-parking-model-testing-smart_parkingpy)
      - [📜 More About Script Operation](#-more-about-script-operation-14)
      - [🛠 Usage](#-usage)
- [🚘 Core Vehicle Functions (`main_func`)](#-core-vehicle-functions-main_func)
  - [🧠 Primary Scripts for Vehicle Control and Visualization](#-primary-scripts-for-vehicle-control-and-visualization)
    - [📜 File Descriptions](#-file-descriptions)
    - [🕹️ Vehicle Control (`custom_control.py`)](#️-vehicle-control-custom_controlpy)
      - [▶️ Launch Command](#️-launch-command-1)
      - [🖥️ Example Console Output](#️-example-console-output-1)
      - [📜 More About Script Operation](#-more-about-script-operation-15)
    - [🪞 Mirror Display (`side_mirror_cameras.py`)](#-mirror-display-side_mirror_cameraspy)
      - [▶️ Launch Command](#️-launch-command-2)
      - [🖥️ Example Console Output](#️-example-console-output-2)
      - [📜 More About Script Operation](#-more-about-script-operation-16)
    - [📷 Telemetry Visualization Camera (`camera_telemetry.py`)](#-telemetry-visualization-camera-camera_telemetrypy)
      - [▶️ Launch Command](#️-launch-command-3)
      - [🖥️ Example Console Output](#️-example-console-output-3)
      - [📜 More About Script Operation](#-more-about-script-operation-17)
    - [🎥 Third-Person Camera View (`third_person_camera.py`)](#-third-person-camera-view-third_person_camerapy)
      - [▶️ Launch Command](#️-launch-command-4)
      - [🖥️ Example Console Output](#️-example-console-output-4)
      - [📜 More About Script Operation](#-more-about-script-operation-18)
    - [👁️ First-Person Camera View (`first_person_camera.py`)](#️-first-person-camera-view-first_person_camerapy)
      - [▶️ Launch Command](#️-launch-command-5)
      - [🖥️ Example Console Output](#️-example-console-output-5)
      - [📜 More About Script Operation](#-more-about-script-operation-19)
- [🌍 Environment Simulation (`world_setup`)](#-environment-simulation-world_setup)
  - [🗺️ Scripts for World Generation, Traffic Management, and Object Control](#️-scripts-for-world-generation-traffic-management-and-object-control)
    - [📜 File Descriptions](#-file-descriptions-1)
    - [🚦 Traffic Generation with Event Simulation (`generate_traffic_with_events.py`)](#-traffic-generation-with-event-simulation-generate_traffic_with_eventspy)
      - [▶️ Launch Command](#️-launch-command-6)
      - [🖥️ Example Console Output](#️-example-console-output-6)
      - [📜 More About Script Operation](#-more-about-script-operation-20)
    - [🚗 Vehicle Spawning from File Coordinates (`spawn_vehicles_from_file.py`)](#-vehicle-spawning-from-file-coordinates-spawn_vehicles_from_filepy)
      - [▶️ Launch Command](#️-launch-command-7)
      - [🖥️ Example Console Output](#️-example-console-output-7)
      - [📜 More About Script Operation](#-more-about-script-operation-21)
    - [🧹 Traffic Cleanup in Simulation (`cleanup_traffic.py`)](#-traffic-cleanup-in-simulation-cleanup_trafficpy)
      - [▶️ Launch Command](#️-launch-command-8)
      - [🖥️ Example Console Output](#️-example-console-output-8)
      - [📜 More About Script Operation](#-more-about-script-operation-22)
    - [🧨 Full Deletion of All Vehicles and Simulation Objects (`destroy_all_vehicles.py`)](#-full-deletion-of-all-vehicles-and-simulation-objects-destroy_all_vehiclespy)
      - [▶️ Launch Command](#️-launch-command-9)
      - [🖥️ Example Console Output](#️-example-console-output-9)
      - [📜 More About Script Operation](#-more-about-script-operation-23)
    - [🚗 Vehicle Creation and Initialization in Simulation (`spawn_vehicle.py`)](#-vehicle-creation-and-initialization-in-simulation-spawn_vehiclepy)
      - [▶️ Launch Command](#️-launch-command-10)
      - [🖥️ Example Console Output](#️-example-console-output-10)
      - [📜 More About Script Operation](#-more-about-script-operation-24)
    - [🗺️ Retrieve Current Coordinates of Active Vehicle (`get_vehicle_coords.py`)](#️-retrieve-current-coordinates-of-active-vehicle-get_vehicle_coordspy)
      - [▶️ Launch Command](#️-launch-command-11)
      - [🖥️ Example Console Output](#️-example-console-output-11)
      - [📜 More About Script Operation](#-more-about-script-operation-25)
    - [🎥 Logging Vehicle Movement and Control Snapshots for Analysis (`record_controls.py`)](#-logging-vehicle-movement-and-control-snapshots-for-analysis-record_controlspy)
      - [▶️ Launch Command](#️-launch-command-12)
      - [🖥️ Example Console Output](#️-example-console-output-12)
      - [📜 More About Script Operation](#-more-about-script-operation-26)
- [🖼️ Media Files (`static`)](#️-media-files-static)
  - [🖼️ Images, GIFs, and Videos Used in the Driver Assistance System](#️-images-gifs-and-videos-used-in-the-driver-assistance-system)
    - [📁 Folder Overview](#-folder-overview)
- [📄 Documentation (`docs`)](#-documentation-docs)
  - [📑 Reports, System Analysis, and Supporting Materials](#-reports-system-analysis-and-supporting-materials)
- [⚙️ Development Environment \& Dependencies](#️-development-environment--dependencies)
  - [Hardware Configuration Used During Development:](#hardware-configuration-used-during-development)
  - [Primary Python Libraries Used:](#primary-python-libraries-used)
- [🙏 Acknowledgements](#-acknowledgements)
  - [🙌 I would like to thank the authors of the following projects:](#-i-would-like-to-thank-the-authors-of-the-following-projects)

---

<br><br><br><br><br>

---

### ❗️ Important Notes for System Operation:

1. **Launching the CARLA Simulator**  
   For the system to function properly, you must first launch the **CARLA simulator** on your device. The simulator must be fully initialized and available for connection.  
   ⚠️ The project was developed and tested with **CARLA version 0.9.14**. Functionality on other versions is not guaranteed.

2. **Spawning a Vehicle**  
   After the simulator has started, you need to create or spawn a vehicle in the simulation. Without this step, the system will not be able to interact with the car.

3. **Enabling Multimedia / Starting Individual Functions**  
   Multimedia functions and related services (such as cameras and sensors) can only be activated after a vehicle has been spawned and is present in the simulation. This is due to the need to connect to sensors and cameras, which require attachment to a vehicle object.

### 📑 Additional README Files

The project also includes several README files that contain brief descriptions of the respective folders and their contents. These files will help you better navigate the project structure and understand the purpose of various system components.

**Each project folder** contains a small README file that explains what files are inside and how they are used. These files are written in both Russian and English for user convenience.

### 📌 Attention When Reading Documentation

Some sections of this README file contain **expandable blocks** (`<details>`) with additional information: function descriptions, code explanations, logic details, and file structure breakdowns.  
🔽 **Be attentive** and expand these blocks to get a complete understanding of the system and its capabilities.

### ❗️ Media File Loading Delay

Please note that **media files (GIFs and images)** demonstrating the operation of various system features may load with a delay. This depends on file size and your internet connection speed.  
Below each media element, there is a small caption with the `⏳` icon indicating that the image or animation might not appear immediately.  
These captions are added specifically so you **don’t miss important functionality demonstrations** if the visual content loads slowly.

---

<br><br><br><br><br>

---

# 🛜 RAAS Modules (raas_func)

---

## 🚘 Logic and Functions of the Intelligent Driver Assistance Platform

This folder contains **all the key modules** that define the behavior and functionality of the driver assistance system.  
Unlike simulation or environment settings, these scripts implement **actual features**, including safety systems, automation, camera operation, and multimedia functionality.

The structure includes separate modules for each feature, emergency handling, camera utilities, and a prototype of the smart parking system.

### 📁 Folder Contents

- **` __pycache__/ `**  
  Automatically generated by Python to cache compiled modules. Not used manually.

- **` recordings/ `**  
  Contains video recordings from vehicle cameras made during emergency events.

  <details>
    <summary>🎥 Incident Recording Information</summary> 

    ⚠️ Camera recordings are not included in the repository (excluded via .gitignore)  
    The project saves **camera footage during detected road incidents**, covering **one minute before and one minute after** the event.  
    These files are saved in the folder:
    ```
    raas_func/recordings/
    ```
    Due to their large size and frequent updates, these videos are **not committed to the repository** — they are excluded via `.gitignore` to simplify work and reduce project size.  
    If needed, you can **download a sample archive with recordings** from the **[Releases](https://github.com/TheAndreyZakharov/Russian-Automotive-Assistance-System/releases)** section.  
    The file ` recordings.zip ` can be found under **Assets** of the latest release.
    
    📥 How to Download  
    Go to:
    ```
    Releases → Latest → Assets → recordings.zip
    ```
    Then extract the archive to the specified directory.

    📁 Where to Place the Recordings  
    After extraction, make sure all video files are located in:
    ```
    raas_func/recordings/
    ```
    This folder **should only contain video files** — do not add extra documents or subfolders.

    🔧 File Paths Remain Valid  
    Although recordings are not included in the repo, **paths in the code remain unchanged**.  
    After extracting the archive, all functionality will work **without editing the code**.
  </details>

- **` smart_parking_train/ `**  
  Folder containing everything needed for training the automatic parking model.

### 📜 Script Descriptions

- **` adaptive_cruise_control.py `**  
  Implements adaptive cruise control.

- **` camera_360_view.py `**  
  Provides a 360-degree view by merging images from multiple cameras.

- **` camera_recorder.py `**  
  Manages video recording and saving from cameras during emergencies.

- **` database_logger.py `**  
  Creates and manages the database (` system_data.db `) for logging events.

- **` driver_fatigue_monitor.py `**  
  Monitors signs of driver fatigue or distraction using video analysis or behavioral data.

- **` emergency_braking.py `**  
  Triggers emergency braking based on sensor readings and situational analysis.

- **` emergency_call_monitor.py `**  
  Automatically contacts emergency services during serious incidents.

- **` lane_keeping_assist.py `**  
  Maintains lane position, warns or corrects deviations.

- **` mirror_alert_toggle.py `**  
  Handles blind spot alerts and mirror signal display.

- **` multimedia_panel.py `**  
  Manages the driver's multimedia interface (audio, visual output, menus, etc.).

- **` smart_parking.py `**  
  Prototype of the smart parking feature — the car searches for a spot and parks itself using a trained model.

- **` system_data.db `**  
  SQLite database file for storing system logs, events, and user data.

This directory is the **core of the entire functional logic** of the driver assistance system. Each module is responsible for a specific **real-world feature that enhances safety, comfort, or automation**.

---

<br>

### 🎛️ RAAS Multimedia Panel (` multimedia_panel.py `)

<p align="center">
    <img src="raas_project/static/media/raas_multimedia.gif" alt="RAAS Multimedia Panel" width="800"/>
</p>
<p align="center"><em>⏳ The GIF may take a few seconds to load — please wait for the animation to appear</em></p>

#### ▶️ Launch Command

```
python multimedia_panel.py
```

#### 🖥️ Example Console Output
```
pygame 2.6.1 (SDL 2.28.4, Python 3.7.0)
Hello from the pygame community. https://www.pygame.org/contribute.html
[] Emergency Call Monitor disabled.
[+] Connected to vehicle: vehicle.lincoln.mkz_2020 (ID 24)
[] Press Q to exit.
```


📁 The GIF shows the main panel interface, including function control, screen navigation, settings, and feature previews.

The multimedia panel is a **centralized graphical user interface (GUI)** implemented using ` PyQt5 `, providing access to the features of the RAAS system.  
It serves as the link between the user and all intelligent vehicle subsystems.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

**Structure and Initialization:**

* The ` RAASPanel ` class inherits from ` QWidget ` and represents the **main application window** with a fixed resolution of ` 1280x720 `.
* On startup:
  - Connects to the CARLA simulator (` localhost:2000 `);
  - Finds the first available vehicle from the actor list (` vehicle.* `);
  - Loads all visual resources (background, icons, GIFs);
  - Launches the camera system (` Camera360 `) and recording buffer (` CameraBufferRecorder `);
  - Initializes other modules: emergency call (` EmergencyCallMonitor `), fatigue monitoring, auto-braking, cruise control, and smart parking.

**Screen Navigation:**

* The panel uses a **stack mechanism (` QStackedWidget `)**:
  - Each screen is a separate ` QWidget ` (e.g., ` main_screen `, ` view360_screen `, ` functions_screen `);
  - Navigation is done via buttons and gestures (e.g., swipe up from the welcome screen);
  - The interface is divided into:
    - **Top bar** — clock and date;
    - **Sidebar** — quick access to apps;
    - **Bottom bar** — music, controls, volume.

**Built-in Modules and Interaction:**

The RAAS panel coordinates **activation and deactivation of functions**, as well as displays their statuses:

- ` Camera360 ` — 360° view mode, automatically activates in reverse or manually;
- ` EmergencyCallMonitor ` — responds to severe collisions and starts a 112 call countdown;
- ` DriverFatigueMonitor ` — monitors driver activity and signals fatigue;
- ` AutoBrakingSystem ` — automatically activates braking during dangerous proximity;
- ` SmartParkingModule ` — detects parking zones and initiates maneuvers;
- ` AdaptiveCruiseControl ` — maintains set speed with automatic braking/acceleration.

Each module can be **enabled or disabled manually** in the "Functions" section. The interface:
- Changes the button color (green — enabled, gray — disabled);
- Displays confirmation before disabling;
- Saves the state to the database.

**360° Camera Mode:**

* Automatically activates in reverse gear;
* Displays a pair: general view (` display_left `) and selected camera (` display_right `);
* Cameras are selected by clicking the transparent region in the view (front, rear, left, right).

**Smart Parking:**

* The panel visualizes feeds from 4 cameras and automatically detects parking opportunities;
* The "Execute Parking" button is active only when a valid parking spot is detected nearby;
* On start, a ` QThread ` runs that step-by-step executes the parking trajectory;
* Manual cancelation is available via the “Stop” button or the ` P ` key.

**Adaptive Cruise Control:**

* Enabled manually from a dedicated screen;
* Allows speed adjustment in 5 km/h increments;
* Automatically brakes when approaching other objects (via CARLA leader vehicle).

**Saved States:**

The panel logs each function state change and system startup/shutdown:

**What is stored in the database?**

1. **Function States Table** — ` function_states `:
   - ` function_name ` — the function name (` lane_assist `, ` mirror_alerts `, ` auto_braking `, etc.);
   - ` state ` — `"ON"` or `"OFF"`;
   - ` timestamp ` — exact date and time of the change.

2. **System Sessions Table** — ` system_sessions `:
   - ` event ` — `"start"` or `"stop"`;
   - ` timestamp ` — the moment the multimedia panel was started or stopped.

This data allows:
- Restoring previous states at next startup;
- Analyzing feature usage by the driver;
- Keeping a full activity history of the system.

</details>

---

<br><br><br>

### 🛣️ Lane Keeping Assist System (` lane_keeping_assist.py `)

<p align="center">
    <img src="raas_project/static/media/raas_line.gif" alt="Lane Keeping Assist Demo" width="1000"/>
</p>
<p align="center"><em>⏳ The GIF may take a few seconds to load — please wait for the animation to appear</em></p>

▶️ **This function is enabled/disabled manually through the multimedia panel in the “Functions” section**.  
📁 The GIF shows an example of the lane keeping system in action, with visualization of deviation and corrective response.

The Lane Keeping Assist system tracks the vehicle’s position relative to the centerline of the lane and, when necessary, **gently corrects steering** to keep the vehicle within its lane.  
This is achieved using a PID controller, and the visualization is rendered in a separate window displaying lane lines and offset from the camera center.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* The function is launched via a standard Python script using the ` pygame ` library for the interface and ` cv2 ` for processing the camera feed.
* An RGB camera is mounted on the vehicle at a height of 2.4 meters and faces forward.
* The interface simultaneously displays real-time parameters: speed, steering angle, gear, turn signals, and the ` Lane Assist ` system status flag.
* The core algorithm works as follows:
  * The camera captures real-time images.
  * Using OpenCV, the lower part of the frame (ROI) is cropped, converted to grayscale, blurred, and passed through a Canny edge detector.
  * ` HoughLinesP ` is then applied to detect potential lane lines. These are split into left and right based on their slope.
  * Visual indicators are used: red for left line, green for right, blue for the camera center, yellow for the calculated lane center.
* A PID controller is used to manage steering, taking the deviation from the lane center as error input.  
  Steering corrections are applied smoothly, factoring in the elapsed time between frames (` dt `).
* When turn signals are active (` Q `, ` E `, ` Z `), the system temporarily disables itself to avoid interfering with the maneuver.
* If the driver has not activated ` Lane Assist `, manual control is allowed using ` A ` / ` D `.
* Exit the program by pressing ` Q ` or closing the Pygame window.

Thus, the script implements a **basic lane keeping assist system**, providing corrective steering input based on visual lane detection and navigation data from CARLA.

</details>

---

<br><br><br>

### ⚠️ Blind Spot Monitoring System (` mirror_alert_toggle.py `)

<p align="center">
    <img src="raas_project/static/media/raas_mirrors.gif" alt="Blind Spot Detection Demo" width="1000"/>
</p>
<p align="center"><em>⏳ The GIF may take a few seconds to load — please wait for the animation to appear</em></p>

▶️ **This function is enabled/disabled manually through the multimedia panel in the “Functions” section**.  
📁 The GIF demonstrates a visual alert triggered when an object is detected in the blind spot by radar data.

The Blind Spot Monitoring system tracks the areas alongside the vehicle using **short-range radars** and displays visual alerts when obstacles are detected.  
This helps warn the driver in time about vehicles or other objects in hazardous areas, especially during lane changes.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* Connects to the CARLA simulator and accesses the nearest vehicle.
* **Two RGB cameras** are mounted: on the left and right sides, angled backward to simulate side-view mirrors.
* Visualization is based on data from these cameras and displayed as a split window (` cv2.imshow `) showing both left and right feeds.
* **Two radars** (left and right) are also installed, with a narrow field of view and a range of 6 meters.
* When an object is detected within the detection zone (up to 10 m) on either side:
  * A warning icon (` alert_icon.png `) is overlaid on the corresponding camera feed;
  * The event is logged in the database.
* The icon is rendered semi-transparently using an alpha channel, displayed in the top left or top right corner.
* The script avoids logging duplicate events — it tracks the last trigger state for each radar.
* Pressing ` Q ` ends the program, shutting down and destroying all camera and radar instances properly.

This results in a **realistic blind spot monitoring system**, which reacts to nearby objects and visually alerts the driver, while logging events for later analysis.

🗂️ **What is stored in the database?**

Each radar trigger is recorded in the ` mirror_alerts ` table of the SQLite database:

* ` side ` — side of the alert (` left ` or ` right `);
* ` timestamp ` — time of object detection.

These records allow for **tracking the frequency and side of obstacle appearances**, and can be used for retrospective analysis or model training and driver behavior analysis.

</details>

---

<br><br><br>

### 🧿 360-Degree Camera View (` camera_360_view.py `)

<p align="center">
    <img src="raas_project/static/media/raas_360_all.gif" alt="360 Camera View Demo" width="800"/>
</p>
<p align="center"><em>⏳ The GIF may take a few seconds to load — please wait for the animation to appear</em></p>

▶️ **This function is automatically activated when reverse gear is engaged** or through the **multimedia panel**, providing the driver with full situational awareness during parking or maneuvering in tight spaces.  
📁 The GIF demonstrates the function menu within the multimedia panel and user interaction.

This feature visualizes a 360-degree view around the vehicle by combining images from four external cameras — front, rear, left, and right.  
The display generates a **single top-down panoramic view**, simulating a real 360° surround system like in modern cars.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* The ` Camera360 ` class is initialized with a reference to ` vehicle `, ` world `, and optionally, a ` CameraBufferRecorder ` object for frame recording.
* In the ` start() ` method:
  * A default RGB camera template is loaded (resolution 320×240, FOV 120°);
  * 4 cameras are positioned:
    - **front**: in front of the vehicle (` yaw=0 `);
    - **back**: at the rear (` yaw=180 `);
    - **left** and **right**: on the sides (` yaw=±90 `);
  * Each camera is attached to the vehicle and begins streaming data to ` camera_callback `.
* In ` camera_callback() `:
  * The image is converted to a NumPy array → RGB → Pygame Surface;
  * Saved in ` self.image_data[key] `;
  * If a recorder is available, the frame is also saved to the buffer.
* The ` get_surface() ` method combines the images:
  * Cameras are interpreted from a bird's-eye view;
  * Frames are distorted: front images taper at the bottom, rear at the top, sides are rotated and trapezoid-warped;
  * A car image (` car_above.jpg `) is placed at the center;
  * The result is a 1000×800 pixel panorama from all sides.
* All transformations are done using OpenCV:
  * Perspective warping (` cv2.getPerspectiveTransform `, ` warpPerspective `);
  * Rotations, mirroring, resizing.
* The ` stop() ` method removes all cameras, stops image reception, and clears the actor list.

Thus, this module simulates a **real 360-degree surround view system**, significantly enhancing driver awareness and reducing the risk of errors during parking.

</details>

---

<br><br><br>

### 🛑 Emergency Braking System (` emergency_braking.py `)

<p align="center">
  <img src="raas_project/static/media/raas_brakes_1_vertical.gif" width="330"/>
  <img src="raas_project/static/media/raas_brakes_2_vertical.gif" width="330"/>
  <img src="raas_project/static/media/raas_brakes_3_vertical.gif" width="330"/>
</p>
<p align="center"><em>⏳ The GIFs (3 total) may take a few seconds to load — please wait for the animations to appear</em></p>

▶️ **This function is enabled/disabled manually through the multimedia panel in the “Functions” section**.  
📁 The GIFs show real moments where the system activated upon detecting obstacles in the vehicle's path.

The Emergency Braking System is responsible for **automatically reducing speed down to a complete stop** if an object is detected at a dangerous distance in front of the vehicle.  
The system relies on LiDAR data and takes into account the vehicle's current speed, the position of the obstacle, and its relative distance.

If an object is detected too close, emergency braking is triggered, helping to prevent a collision.  
Additionally, the **camera video recording module** is automatically activated to archive the situation (before and after braking).

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* The ` AutoBrakingSystem ` class is initialized with access to the current CARLA ` world ` and ` vehicle `, and optionally the RAAS panel.
* The ` start() ` method initializes the LiDAR sensor:
  - Range — up to 50 meters;
  - Frequency — 20 Hz;
  - Point density — up to 300,000 points per second.
* Data processing is handled in the ` lidar_callback() ` method:
  - Each LiDAR point is used to calculate the distance to nearby objects;
  - If an object in front is closer than the critical threshold — braking is initiated.
* When triggered:
  - The vehicle's speed is reduced to zero (` apply_emergency_brake `);
  - Event data is logged to the database;
  - If the 360° camera module with recording is connected — video capture is started.
* Once the vehicle is fully stopped and 1 second has passed — the brake is released (` release_brake `).
* The ` stop() ` method shuts down the sensor and returns control to the user.

🗂️ **What is stored in the database?**

Each emergency braking event is recorded in the ` emergency_brakes ` table:

- ` timestamp ` — time of activation;
- ` speed_kmh ` — vehicle speed at the moment of activation;
- ` distance_m ` — distance to the obstacle that triggered braking.

This data serves as the basis for **analyzing road situations, safety reports, and verifying the system's performance**.

</details>

---

<br><br><br>

### 🚨 Automatic Emergency Call System (` emergency_call_monitor.py `)

<p align="center">
  <img src="raas_project/static/media/raas_call_accept.gif" width="500"/>
  <img src="raas_project/static/media/raas_call_cancel.gif" width="500"/>
</p>

<p align="center">
  <img src="raas_project/static/media/raas_call_auto.gif" width="500"/>
</p>

<p align="center"><em>⏳ The GIFs (3 total) may take a few seconds to load — please wait for the animations to appear</em></p>

▶️ **This function is enabled/disabled manually through the multimedia panel in the “Functions” section**.  
📁 The GIFs show possible scenarios: manual call confirmation, user cancellation, and automatic dialing after 60 seconds of inactivity.

The emergency call module in RAAS is designed to **respond to potential road accident situations**.  
When sudden braking and/or sharp direction changes are detected, the system logs a potential crash and prompts the driver to confirm a call to emergency number 112.  
If no response is received within 60 seconds, the call is placed automatically.

This system is aimed at **enhancing driver safety in critical situations** and closely integrates with the 360° camera system to trigger video recording for post-event analysis.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* The ` EmergencyCallMonitor ` class is launched as a widget within the multimedia panel.
* In the constructor (` __init__ `), threshold values are defined:
  * ` speed_drop_threshold ` — minimum speed drop for activation (default 30 km/h);
  * ` angle_change_threshold ` — minimum heading change (default 60 degrees).
* A ` QTimer ` checks the vehicle's status every 0.2 seconds (` monitor_vehicle() `):
  * If a sudden speed drop and/or direction change occurs — the system logs a potential accident.
* When triggered, a graphical window opens:
  * The user is prompted to confirm or cancel the call;
  * A 60-second countdown starts simultaneously;
  * If there is no user response — the system automatically dials emergency services.
* Upon call confirmation or cancellation:
  * All incident parameters (speeds, angles, coordinates) are logged to the database;
  * The call result is also recorded: whether it was made or canceled;
  * If the 360° camera system is active, video recording is started.
* The function can be stopped via the ` stop() ` method, which halts all timers and hides the window.

🗂️ **What is stored in the database?**

Each activation of the system is recorded in the ` emergency_calls ` table:

- ` timestamp ` — time the incident was detected;
- ` speed_before ` and ` speed_after ` — speed before and after the event;
- ` speed_drop ` — difference between them;
- ` yaw_before ` and ` yaw_after ` — heading angles before and after the event;
- ` yaw_change ` — total heading change;
- ` duration_sec ` — time elapsed before user response;
- ` location_x `, ` location_y `, ` location_z ` — coordinates at the time of the incident;
- ` call_made ` — ` 1 ` if the call was made, or ` 0 ` if canceled.

This data is used for **report generation, accident analysis, and documenting safety system performance**.

</details>

---

<br><br><br>

### 🛣️ Adaptive Cruise Control (` adaptive_cruise_control.py `)

<p align="center">
    <img src="raas_project/static/media/raas_cruise.gif" alt="Adaptive Cruise Control Demo" width="1000"/>
</p>

<p align="center"><em>⏳ The GIF may take a few seconds to load — please wait for the animation to appear</em></p>

▶️ **This function is launched via the RAAS multimedia control panel.**  
📁 The GIF shows the function's interface within the multimedia system and how it is operated.

This feature enables automatic maintenance of a set vehicle speed, taking into account the current speed and driver input.  
**Adaptive Cruise Control is activated through the RAAS multimedia panel**, allowing for smooth acceleration and braking depending on driving conditions.

The system helps **reduce driver workload on straight roads**, supports safety, deactivates when braking manually, and logs its activity to a database.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* The ` AdaptiveCruiseControl ` class is initialized with references to the ` vehicle ` object and the CARLA ` world `.
* By default, the system is disabled (` self.enabled = False `), with target speed and minimum distance initialized.
* Setting and adjusting the target speed:
  * The ` set_target_speed(speed_kmh) ` method sets the cruise speed (30–150 km/h);
  * ` increase_speed() ` and ` decrease_speed() ` adjust it in 5 km/h increments.
* Cruise control is activated via ` enable() `, which:
  * Logs the event to the database;
  * Displays a console message.
* When braking manually or when explicitly disabled, ` disable() ` is called — cruise control stops and logs the event.
* The ` update() ` method is called in the main vehicle control loop and runs only if the system is enabled:
  * Manual braking disables the system;
  * Manual acceleration (beyond the target speed) is ignored;
  * Otherwise — the system adjusts throttle and brake to approach the target speed.
* Control is applied to the vehicle via ` vehicle.apply_control() `, preserving other parameters (` steering `, ` gear `, ` handbrake `, etc.).
* A placeholder method ` get_closest_vehicle_ahead() ` is available for future expansion to full adaptive cruise functionality, maintaining distance from vehicles ahead.

🗂️ **What is stored in the database?**

When cruise control is enabled or disabled, the system automatically logs data into the ` cruise_control ` table in the SQLite database:

- ` action ` — type of event: `'enabled'` or `'disabled'`;  
- ` timestamp ` — date and time of the event;  
- ` speed_kmh ` — actual vehicle speed at the time of activation/deactivation.

This is used to **track cruise control activation history**, analyze driver behavior, generate reports, and perform system audits.

</details>

---

<br><br><br>

### 🛣️ Driver Fatigue Monitoring (` driver_fatigue_monitor.py `)

<p align="center">
    <img src="raas_project/static/media/raas_fatigue.gif" alt="Driver Fatigue Monitor Demo" width="800"/>
</p>

<p align="center"><em>⏳ The GIF may take a few seconds to load — please wait for the animation to appear</em></p>

▶️ **This function is enabled/disabled manually via the multimedia panel in the “Functions” section.**  
📁 The GIF demonstrates one example of a driver notification when the system detects prolonged inactivity, reminding the driver to take a break.

The driver fatigue monitoring function observes driver behavior behind the wheel, detecting signs of fatigue based on actions such as frequent sharp steering, repeated lane departures without signaling, long periods of uninterrupted driving, and lack of response to autopilot or cruise control.  
**Driver fatigue monitoring is activated/deactivated manually through the RAAS system’s multimedia panel.**

When potential signs of fatigue are detected, the system will **issue a warning to the driver** and log the events to a database for further analysis.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* The ` DriverFatigueMonitor ` class is initialized with references to the ` vehicle ` object and, optionally, the GUI to display alerts.
* Several internal variables are maintained:
  - ` trip_start_time `: time the trip started;
  - ` last_driver_input_time `: last time the driver performed an input;
  - ` last_steer `: last recorded steering values for detecting abrupt movements.
* The ` update_driver_input ` method processes:
  - Driver inactivity for more than 60 seconds;
  - Monitoring of active cruise control and lane keeping systems;
  - Continuous driving over 100 minutes.
* If the driver makes frequent sharp steering inputs or crosses lane markings without turn signals, the system **triggers a warning**.
* Other contributing factors include the presence of active autopilot or cruise control systems.
* Each warning is logged to the database via the ` log_fatigue_warning ` method.

🗂️ **What is stored in the database?**

For every fatigue-related event, the system stores information in the ` fatigue_warnings ` database table:

- ` timestamp ` — precise timestamp of the event;
- ` reason ` — reason for the warning (e.g., "No driver input" or "Frequent sharp steering");
- ` category ` — event category, such as: `"no_input"` (no input), `"long_drive"` (long driving), `"steering"` (sharp turns).

These records are essential for **analyzing driver behavior**, compiling fatigue statistics, and generating reports on driver assistance system performance.

</details>

---

<br><br><br>

### 🎥 Emergency Camera Recording (` camera_recorder.py `)

<p align="center">
    <img src="raas_project/static/media/raas_record_1_cameras.gif" alt="Emergency Camera Recording Demo" width="800"/>
</p>

<p align="center"><em>⏳ The GIF may take a few seconds to load — please wait for the animation to appear</em></p>

This function enables automatic video recording from the vehicle's cameras during emergency events.  
It preserves footage **before and after the incident**, including visual data, timestamps, and the vehicle's current speed.

▶️ **This function is enabled/disabled manually via the multimedia panel in the “Functions” section.**  
📁 The GIF shows an example of the system in action. Full video recordings are available for download in the **Releases** section of the repository.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* The ` CameraBufferRecorder ` class is initialized with the following parameters:
  - ` camera_keys ` — a list of camera names (e.g., `'front'`, `'back'`);
  - ` fps ` — frame rate (default is 30);
  - ` buffer_seconds ` — duration of the pre-event buffer (default is 60 seconds);
  - ` post_seconds ` — duration of post-event recording (default is 60 seconds).
* On start, it connects to the CARLA simulator and locates the first available vehicle.
* A ring buffer ` deque ` is created for each camera, limited by duration (` buffer_seconds × fps `), where frames are stored with:
  - timestamp;
  - current vehicle speed (in km/h).
* The ` add_frame(key, frame) ` method is called by each camera module to add a new frame to the respective buffer.
* When an event is triggered (` trigger_event_recording() `):
  * buffered footage is saved locally;
  * post-event recording begins in parallel;
  * all frames (before and after) are merged;
  * each frame is overlaid with:
    - date and time;
    - current speed;
  * a `.mp4` file is generated, named by date (` YYYYMMDD_HHMMSS_key.mp4 `), and saved in the ` recordings/ ` directory.
* Videos are encoded using ` cv2.VideoWriter `, with resizing applied as needed, and the `'mp4v'` codec is used.

This system provides **continuous video monitoring**, with the ability to save footage **before and after critical moments**, similar to real automotive "black box" systems.

</details>

---

<br><br><br>

### 🅿️ Test Functionality: Smart Parking (` smart_parking.py `)

<p align="center">
    <img src="raas_project/static/media/raas_parking.gif" alt="Smart Parking Demo" width="1000"/>
</p>

<p align="center"><em>⏳ The GIF may take a few seconds to load — please wait for the animation to appear</em></p>

▶️ **This function is enabled/disabled manually through the multimedia panel.**  
📁 The GIF shows an example of the system automatically detecting parking spots with visual markings and zone recognition.

The Smart Parking system implements a **test functionality for intelligent parking spot detection and autonomous maneuver execution**, based on camera input, predefined parking coordinates, and pre-recorded motion paths.  
The mode actively uses real-time image processing to determine the presence of a valid parking zone and, if found, carries out the parking maneuver without driver involvement.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* The ` SmartParkingModule ` class is initialized with ` world ` and ` vehicle ` objects from CARLA.
* **Four cameras** (front, rear, left, right) with a 120° field of view are set up, whose feeds are used for visual analysis.
* A list of predefined **parking spot coordinates** (` PARKING_SPOTS `) is initialized, and availability is determined by distance from the vehicle:
  * If the distance to a point is less than 8 meters — the spot is considered available.
* Upon detecting a parking zone on the correct side (left or right), the system visually marks the area and updates its state.

**Image Processing:**
* Color masks (white and yellow lines) are used;
* Lane lines are detected via ` cv2.HoughLinesP `;
* A center of mass is calculated to identify the zone, and a visual indicator is centered on the screen.

**Parking Execution:**
* A corresponding ` pathX.json ` is loaded, where X is the parking spot ID;
* The vehicle first approaches the starting point of the path;
* Then, in real-time:
  * Time-stamped data is read;
  * Control values — ` throttle `, ` steer `, ` brake `, ` gear `, etc. — are applied from the file;
  * Movement is synchronized with ` world.tick() ` in CARLA.
* The maneuver can be **manually interrupted** at any time (e.g., via the UI button).
* Upon completion, the script applies brakes and logs the parking completion.

🗂️ **What is stored in the database?**

At the start and end of the parking process, the system logs data to the ` smart_parking ` database table:

* ` action ` — `'start'` at the beginning and `'stop'` at the end of the parking maneuver;
* ` timestamp ` — the event's timestamp;
* ` side ` — parking side (` left ` or ` right `), depending on the detected space.

These records allow the system to **track when and from which side parking attempts occurred**, and provide data for later analysis or training models.

</details>

---

<br><br><br>

### 🗃️ Working with the Database (` database_logger.py `)

This module provides a logging system for various events and states during the operation of the RAAS system, storing data in a SQLite database.  
The database is used to **track the status of system functions, multimedia events**, and other critical parameters such as emergency braking, mirror radar alerts, cruise control, and more.

The system helps **retain data about critical moments** in the system's operation and enables analysis and auditing of the vehicle and driver assistance features.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* The ` DatabaseLogger ` class creates a connection to a SQLite database and initializes several tables to store data:
  - ` function_states `: logs the enable/disable status of system functions;
  - ` system_sessions `: stores start and end events of multimedia sessions;
  - ` mirror_alerts `: logs radar alerts for blind spot detections;
  - ` emergency_brakes `: stores emergency braking events including speed and object distance;
  - ` cruise_control `: tracks cruise control state changes;
  - ` smart_parking `: logs smart parking activity;
  - ` emergency_calls `: logs emergency call data (speed, yaw, duration, location);
  - ` fatigue_warnings `: logs driver fatigue warnings.

* When an instance of the class is created, it connects to the database and creates the tables if they do not already exist.

* All logged data is stored in the database tables with timestamps:
  - For each event, the system records:
    - ` timestamp `: the exact time the event occurred;
    - additional parameters (e.g., speed, function state, location, etc.).

* Example methods for logging events:
  - ` log_function_state(function_name, state) `: logs a function's state (e.g., "enabled" or "disabled");
  - ` log_system_event(event) `: logs multimedia session events ("start" or "stop");
  - ` log_mirror_alert(side) `: logs mirror radar alerts (left or right);
  - ` log_emergency_brake(speed_kmh, distance_m) `: logs emergency braking events, including speed and object distance;
  - ` log_cruise_control(action, speed_kmh) `: logs cruise control activation/deactivation;
  - ` log_smart_parking(action, side=None) `: logs smart parking events (start/stop and side);
  - ` log_emergency_call(...) `: logs emergency call data, including speed, angles, and location;
  - ` log_fatigue_warning(reason, category) `: logs driver fatigue warnings.

* The ` get_last_states() ` method retrieves the latest states of all system functions, allowing real-time status checks.

* To prevent concurrent access issues, database operations are thread-safe using ` threading.Lock() `.

This system **collects detailed information about the operation of all core components** of the driver assistance system and provides capabilities for analysis, auditing, and further optimization of all subsystems.

</details>


---

<br><br><br>

### 🗂️ Smart Parking (` smart_parking_train `)

#### 🚗 Autonomous Vehicle Parking Using a Custom Dataset and Neural Network

This folder contains all components necessary for **training, evaluating, and testing** a deep learning model for automatic parking.  
It includes data collection tools, the dataset itself, training scripts, saved models, and utilities for visualizing the results.

The folder structure represents the full model development cycle:  
from **data recording** ➝ to **training** ➝ to **testing** ➝ and **result analysis**.


### 📁 Folder Contents

- **` __pycache__/ `**  
  Automatically generated by Python for caching compiled modules. Not used manually.

- **` dataset/ `**  
  Contains the full dataset used for training — camera images and a telemetry CSV file.

    <details>
        <summary>📂 Dataset Information</summary> 

    📂 Parking Dataset  

    🧪 Custom dataset for training the automatic parking model  

    This folder contains a **self-collected dataset** used for training a model that performs automatic parking.  

    Data was gathered during manual parking sessions using cameras and sensors in various scenarios.  

    The dataset includes **camera images** and **telemetry data**, making it suitable for both computer vision and sensor data analysis.

    📁 Dataset Structure:
    - **` log.csv `**  
      A CSV file with synchronized telemetry data, including:
      - ` frame `: Frame number  
      - ` throttle `: Acceleration  
      - ` steer `: Steering angle  
      - ` brake `: Braking  
      - ` speed `: Vehicle speed  
      - ` front_dist `, ` back_dist `, ` left_dist `, ` right_dist `: Distances to obstacles  

    This file contains numerical control and sensor data for supervised model training.

    - **` images/ `**  
      Folder with images captured by the vehicle’s cameras during parking sessions.  
      Each image corresponds to a frame in ` log.csv ` and provides visual context.

    📸 Image Dataset Info  
    ⚠️ The image dataset is not included in the repository (excluded via `.gitignore`)  

    A custom **image dataset of over 13,000 PNG files (~1.5 GB)** was created.  
    To avoid exceeding GitHub’s storage and performance limits, the image folder is **excluded from version control using `.gitignore`**.  

    Therefore, the images are **not tracked by Git** and **not included in the repo**, but the code still expects them to be in the correct local directory.

    📥 To download:
    ```
    Releases → Latest → Assets → images.zip
    ```  
    Then extract the archive locally.

    📁 Image Placement  
    After extraction, ensure that **all PNG images are in the same folder as this `README.md` file**.  
    This folder **should contain only images** — no extra files or subfolders.

    🔧 Paths remain valid  
    Although the images are not committed, **paths in the code remain unchanged**.  
    Once extracted, the training script:
    ```
    raas_func/smart_parking_train/train_model.py
    ```
    will work **without requiring path changes**, assuming images are placed correctly.

    This dataset is crucial for supervised learning tasks that aim to **map sensor data, images, and vehicle behavior during parking**.

    </details>

- **` models/ `**  
  Stores trained models, including multiple variants and architectures tested.

    <details>
        <summary>📂 Model Files Information</summary> 

    ⚠️ Trained models are not included in the repository (excluded via `.gitignore`)  

    Models used for automatic parking were trained for this project.  
    Since their size **exceeds GitHub's limits**, model files are **not included in the repo** and are **excluded via `.gitignore`**.

    📥 To download:
    ```
    Releases → Latest → Assets → models.zip
    ```
    Then extract the archive locally.

    📁 File Placement  
    Ensure **all model files are in the same folder as this `README.md`**.  
    This folder **should contain only model files** — no extra documents or folders.

    🔧 Paths remain valid  
    Although model files are not committed, **code paths remain unchanged**.  
    All related code will work **without path adjustments** as long as files are placed correctly.

    </details>

- **` plot_results/ `**  
  Contains charts, logs, and visualizations from model training.

    <details>
        <summary>📂 Training Results and Plots</summary> 

    📂 Training Results and Plots  
    📊 Visualization and logs from the model training process  

    This folder contains scripts, logs, and charts illustrating the training process of the smart parking model.  
    It serves as a **metrics archive**, helping to monitor progress, detect issues, and analyze model behavior over time.

    📁 File Descriptions:
    - **` train_log.txt `**  
      Log file with epoch-wise training data, including loss values and other metrics.
    - **` plot_training.py `**  
      Script for parsing ` train_log.txt ` and generating training charts.
    - **` loss_plot.png `**  
      Loss over epochs chart.
    - **` training_detailed_plot.png `**  
      A more detailed training progression chart.

    📜 Script Descriptions:
    - **` record_data.py `**  
      Records data from the vehicle (camera and sensors) during manual parking. Saves to ` dataset/ `.
    - **` train_model.py `**  
      Trains the model using the collected dataset.
    - **` smart_parking.py `**  
      Prototype script that uses the trained model to autonomously park the vehicle.  

    </details>

This directory is the **foundation of the smart parking system's development**, integrating data collection, model training, and real-world testing.

---
<br><br>

### 📊 Training Results Visualization and Analysis (` plot_training.py `)

<p align="center">
    <img src="raas_project/raas_func/smart_parking_train/plot_results/training_detailed_plot.png" alt="Training Curve Plot" width="800"/>
</p>

<p align="center"><em>⏳ The image may take a few seconds to load — please wait for it to appear</em></p>

This script is designed to **analyze model training logs**, extract key metrics, and visualize the trends of training and validation losses.  
It helps **visually assess training performance, detect overfitting or underfitting**, and identify which epochs triggered model checkpoint saving.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* The script reads the ` train_log.txt ` file, which contains the model's training log with the expected structure:
  * ` --- Epoch X ` — marks the beginning of a new epoch;
  * ` Train Loss: ... | Val Loss: ... ` — loss metrics for the current epoch;
  * `[+] New best model saved` — indicates a model checkpoint was saved;
  * `[!] No improvement. Patience: ...` — indicates early stopping logic is being applied.
* It extracts:
  * ` train_losses ` and ` val_losses ` values;
  * ` best_epochs ` — epoch numbers when models were saved;
  * patience counters (if present);
  * total training time (parsed from the ` Training finished in ... ` line).

**Plotting the Graph:**
* Trend lines for ` Train Loss ` and ` Validation Loss ` are displayed;
* Checkpoints are marked with **green stars**;
* The best (final saved) model is marked with a **red star**;
* The graph corner includes:
  * total number of epochs;
  * best epoch number and its validation loss;
  * total training duration.

**Saving:**
* The resulting graph is saved as ` training_detailed_plot.png ` next to the script;
* It also opens in an interactive window via ` plt.show() `.

</details>

---

<br><br><br>

### 🎥 Custom Dataset Recording (` record_data.py `)

This script allows you to **collect your own dataset for training computer vision or control models** using the CARLA simulator.  
It automatically records images from four cameras (front, back, left, right), radar data, vehicle control parameters (throttle, brake, steering), and current speed.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* The ` DataCollector ` class initializes a connection to CARLA, selects the active vehicle, and sets up sensors:

  * 4 RGB cameras (front, back, left, right) mounted around the vehicle;
  * 4 radars oriented in the same directions to detect distances to nearby objects.

* All data is saved as follows:

  - 📂 ` dataset/images/ ` — images from the cameras, named using the format ` front_00005.png `, ` left_00005.png `, etc.;
  - 📄 ` dataset/log.csv ` — a metadata table for each recorded frame.

* For each ` frame `, the following values are stored in the CSV file:

  | Parameter       | Description                            |
  |------------------|----------------------------------------|
  | ` frame `        | Frame number                           |
  | ` throttle `     | Throttle value                         |
  | ` steer `        | Steering position                      |
  | ` brake `        | Brake value                            |
  | ` speed `        | Current speed (m/s)                    |
  | ` front_dist `   | Distance to the object in front (m)    |
  | ` back_dist `    | Distance to the object behind (m)      |
  | ` left_dist `    | Distance to the object on the left     |
  | ` right_dist `   | Distance to the object on the right    |

* Frames are captured at intervals defined by ` SAVE_EVERY_N_FRAMES ` (default: every 5th frame).
* Driving is manual — the user operates the vehicle, and the system logs everything in the background.
* A Pygame window displays the current frame number to monitor recording progress.

**Stopping:**

To stop recording, simply press ` ESC `. All sensors will shut down, connections will close, and the CSV file will be saved.

</details>

---

<br><br><br>

### 🧠 Training the Smart Parking Model (` train_model.py `)

This module is used to **train a neural network model** capable of controlling a vehicle during parking maneuvers, using images from four cameras and radar readings.  
Training is performed on a custom dataset collected in the CARLA simulation, with the best model saved based on the ` val loss ` metric.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

**Dataset and Preprocessing:**

* Uses a custom ` ParkingDataset ` class to read:
  - Images from the ` dataset/images ` folder, using masks like ` front_*.png `, ` back_*.png `, etc.;
  - Log data from ` dataset/log.csv ` (including ` throttle `, ` steer `, ` brake `, and radar data).
* Image transformations include:
  - Scaling and random cropping;
  - Color jittering (` ColorJitter `);
  - Normalization using ImageNet statistics;
* For each frame, four images are concatenated into a 12-channel tensor, combined with four radar values.

**Model: ` MultiCamNet `**

* The core of the model is a ` ResNet34 ` with the final layer removed (` avgpool ` used separately for each image);
* Features from each camera are concatenated (total size: 2048);
* Four radar values are added;
* Followed by a fully connected network (256 → 128 → 3) predicting ` throttle `, ` steer `, and ` brake `.

**Training Process:**

* Utilizes:
  - ` SmoothL1Loss ` as the loss function;
  - ` Adam ` optimizer;
  - ` CosineAnnealingLR ` scheduler to gradually reduce the learning rate.
* After each epoch:
  - Average ` val loss ` is calculated;
  - If improved — the model is saved as ` best_model.pth `;
  - If no improvement for ` PATIENCE ` epochs — training stops early (early stopping).

**Visualization:**

* At the end of training, a graph of ` Train Loss ` and ` Validation Loss ` is generated and saved as ` loss_plot.png ` in the ` plot_results ` folder.

</details>

---

<br><br><br>

### 🤖 Smart Parking Model Testing (` smart_parking.py `)

This function allows you to **test the trained neural network model in real time**, performing automatic parking maneuvers.  
The model controls the vehicle in the CARLA simulation using input from four cameras (front, back, left, right) and directional radar sensors.

▶️ **Activate the function by pressing the ` P ` key** during the simulation. Press ` P ` again to stop.  
To exit the test, press ` ESC `.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* The ` SmartParking ` class launches the system by connecting to the nearest vehicle in CARLA and activating sensors:
  - 4 RGB cameras (oriented forward, back, left, right);
  - 4 radars to measure distance to surrounding objects;
  - A Pygame interface to visually display live camera feeds.

* The trained model ` MultiCamNet ` is loaded from disk (path: ` best_model.pth `) and used to predict ` throttle `, ` steer `, and ` brake ` values.

* Data preprocessing includes:
  - Resizing all images to ` 320x240 `;
  - Normalization (mean and std per channel);
  - Combining the four images into a single tensor.

* The model receives two inputs:
  - ` img_tensor ` — concatenated camera images;
  - ` radar_tensor ` — 4 distance values from the radars.

* Control is applied to the vehicle using ` vehicle.apply_control()`:
  - Values (` throttle `, ` steer `, ` brake `) are slightly amplified for better responsiveness;
  - A minimum throttle value is enforced to prevent early halting.

* The UI displays the four camera views in a ` 2x2 ` matrix layout.

#### 🛠 Usage

1. Start the script while near a vehicle in the CARLA simulation;
2. Press ` P ` to activate smart parking;
3. Press ` P ` again to stop;
4. Press ` ESC ` to exit the program.

</details>

---


<br><br><br><br><br>

---

# 🚘 Core Vehicle Functions (` main_func `)

---

## 🧠 Primary Scripts for Vehicle Control and Visualization

This folder contains the **core modules** responsible for vehicle control and camera handling.  
These scripts enable driver interaction with the vehicle and perception of the surrounding environment.

They serve as the **foundation** of the driver assistance system and include:
- Vehicle control mechanisms  
- Mirror and camera operations  
- Various viewing modes (first-person, third-person, telemetry)

### 📜 File Descriptions

- **` custom_control.py `**  
  Handles the vehicle control logic.

- **` side_mirror_cameras.py `**  
  Sets up the side mirror displays.

- **` first_person_camera.py `**  
  Implements the first-person camera view.

- **` third_person_camera.py `**  
  Provides a third-person camera perspective.

- **` camera_telemetry.py `**  
  Displays vehicle telemetry through a dedicated camera.

---

<br>

### 🕹️ Vehicle Control (` custom_control.py `)

<p align="center">
    <img src="raas_project/static/media/main_control.gif" alt="Custom Control Demo" width="1000"/>
</p>

<p align="center"><em>⏳ The GIF may take a few seconds to load — please wait for the animation to appear</em></p>

#### ▶️ Launch Command
```
python custom_control.py
```

#### 🖥️ Example Console Output
```
pygame 2.6.1 (SDL 2.28.4, Python 3.7.0)
Hello from the pygame community. https://www.pygame.org/contribute.html
[+] Connected to: vehicle.lincoln.mkz_2020

================= CONTROLS =================
W - Throttle (Forward)
S - Brake / Reverse (if stopped)
A / D - Steer Left / Right
Space - Handbrake
M - Toggle Manual Gear Mode
R / N / 1-6 - Select Reverse / Neutral / Gear
Q / E / Z - Turn Signals (Left / Right / Hazard)
L - Toggle Headlights
P - Toggle Autopilot
C - Change Weather Preset
Esc or Ctrl+C - Exit
```


This script provides manual vehicle control via keyboard using the Pygame interface.  
It allows testing vehicle behavior in simulation without autopilot, including gear shifting, manual throttle/brake, steering, lights, and weather changes.

It is the main module for **interactive real-time vehicle control**, useful for debugging driving logic, training models, or visually testing simulation scenarios.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

- The script starts by initializing Pygame: a 400x300 window is created to display a control/status panel.
- A connection is established with CARLA (` carla.Client `), with a 10-second timeout, and the current ` world ` is retrieved.
- A list of ` vehicle.* ` actors is queried, and the first available vehicle is selected. If none is found, the script exits.
- A ` carla.VehicleControl ` object is created for sending control inputs.
- Flags are initialized: ` autopilot_enabled `, ` manual_gear `, and vehicle lights (` VehicleLightState `).
- The main loop:
  - Each frame, Pygame events and key presses are read.
  - Depending on ` manual_gear ` flag, control logic is split into:
    - **automatic gear mode**, with direct throttle/brake control;
    - **manual gear mode**, where gear is manually selected and automatic shifting is disabled.
  - Steering is handled via ` A ` / ` D ` keys.
  - Handbrake toggles with ` SPACE `; turn signals with ` Q `, ` E `, ` Z `.
  - Headlights (` L `) and autopilot (` P `) toggle with a short delay (` sleep(0.2) `) to avoid multiple triggers.
  - Weather conditions cycle via ` C ` through a predefined ` weather_presets ` list.
  - In manual mode, gear is set with ` R `, ` N `, ` 1-6 `, and the ` manual_gear_shift ` flag is set.
- At the end of each iteration:
  - ` vehicle.apply_control(control) ` sends the current control input;
  - ` vehicle.set_light_state() ` updates lighting;
  - The UI displays:
    - speed in km/h;
    - throttle and brake values;
    - current gear;
    - status of autopilot, signals, and headlights.
- The display is refreshed via ` pygame.display.flip() ` at 30 FPS (` clock.tick(30) `).
- On exit (via ` Esc ` or ` Ctrl+C `), ` pygame.quit() ` is called to properly close the window and connection.

This script provides **full manual control of the vehicle with real-time feedback**, enabling hands-on testing of basic driving modes within the CARLA simulator.

</details>

---

<br><br><br>

### 🪞 Mirror Display (` side_mirror_cameras.py `)

<p align="center">
    <img src="raas_project/static/media/main_mirrors.gif" alt="Mirror Cameras Demo" width="1000"/>
</p>

<p align="center"><em>⏳ The GIF may take a few seconds to load — please wait for the animation to appear</em></p>

▶️ **This function is enabled/disabled manually via the multimedia panel in the “Functions” section.**  

#### ▶️ Launch Command
```
python side_mirror_cameras.py
```

#### 🖥️ Example Console Output
```
[+] Vehicle found: vehicle.lincoln.mkz_2020 (ID 24)
[*] Mirror cameras are active. Press Q to exit.
```


This function activates two side cameras mounted on both sides of the vehicle and displays live feeds from the virtual rear-view mirrors.  
It provides **enhanced visibility of blind spots and rear-side areas**, mimicking real automotive mirrors.  
This visualization is especially useful for parking, lane changes, and simulating driver awareness.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* A connection is established with the CARLA simulator (` localhost:2000 `), retrieving the ` world ` and ` blueprint_library `.
* The script filters for ` vehicle.lincoln.mkz_2020 ` actors and selects the one with the lowest ID. If none are found, execution is stopped.
* An RGB camera blueprint is configured with:
  * 640×480 resolution;
  * 90-degree field of view.
* Two transforms are defined (position and rotation) for the cameras:
  * Left camera: rear-left side at -150°;
  * Right camera: rear-right side at +150°.
* Both cameras are spawned and attached to the vehicle using ` world.spawn_actor(..., attach_to=vehicle) `.
* Streamed frames from each camera are processed via ` camera_callback `:
  * The image buffer is converted into a NumPy array;
  * RGB channels are extracted (alpha is discarded);
  * The image is horizontally flipped (` cv2.flip(..., 1) `) to match the real mirror view;
  * The result is stored in the ` image_data ` dictionary under keys `'left'` and `'right'`.
* In the main loop:
  * When both camera feeds are available, they are concatenated horizontally (` cv2.hconcat `) and displayed in an OpenCV window.
  * The loop continues until the ` Q ` key is pressed.
* On exit:
  * Both cameras stop streaming (` .stop()`), are removed from the simulation (` .destroy()`), and all OpenCV windows are closed (` cv2.destroyAllWindows()`).

This module provides a **realistic mirror view simulation**, enhancing environmental awareness around the vehicle and delivering critical visual information for driver or autonomous decision-making.

</details>

---

<br><br><br>

### 📷 Telemetry Visualization Camera (` camera_telemetry.py `)

<p align="center">
    <img src="raas_project/static/media/main_telemetry.gif" alt="Telemetry" width="800"/>
</p>

<p align="center"><em>⏳ The GIF may take a few seconds to load — please wait for the animation to appear</em></p>

#### ▶️ Launch Command
```
python camera_telemetry.py
```

#### 🖥️ Example Console Output
```
[+] Vehicle found: vehicle.lincoln.mkz_2020 (ID 24)
[*] 3rd person camera with full telemetry is active. Press Q to exit.
```


This function activates a third-person camera positioned behind the vehicle and **overlays real-time telemetry on the camera feed**.  
On-screen information includes: steering angle, throttle, brake, current speed (in km/h), and gear position.  
It allows **visual monitoring of vehicle behavior in motion**, which is useful for debugging and control system testing.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

- Connects to the CARLA simulator at ` localhost:2000 ` and requests the current ` world ` and ` blueprint_library ` — a list of available sensors and actors.
- Searches for active vehicles with the filter ` vehicle.lincoln.mkz_2020 ` and selects the one with the lowest ID. If none is found, the script exits.
- An RGB camera (` sensor.camera.rgb `) is created with:
  - Resolution: 640×480;
  - Field of view: 90°;
  - Positioned behind the vehicle at ` Transform(x=-10, y=0, z=4) `.
- The camera is attached to the vehicle and starts streaming frames asynchronously via `.listen()`. Each frame is handled by ` camera_callback `:
  - The raw image buffer is converted to a NumPy array;
  - Only RGB data is extracted;
  - The result is stored in the ` image_data ` dictionary under the key `'back'`.
- The main loop:
  - Checks for the latest camera frame;
  - If a new frame is available, a copy is made and telemetry is overlaid:
    - ` Steering ` — current steering input;
    - ` Throttle ` and ` Brake ` — acceleration and braking;
    - ` Speed ` — calculated from the vehicle’s velocity vector and converted to km/h;
    - ` Gear ` — current gear, displayed as ` R `, ` N `, or a number.
  - All telemetry is rendered on the frame using OpenCV (` cv2.putText `) and displayed in a window.
- The loop continues until the user presses ` Q `.
- On exit:
  - The camera stream is stopped and destroyed (` stop() `, ` destroy()`),
  - All OpenCV display windows are closed (` cv2.destroyAllWindows()`).

This script provides a **third-person camera view with real-time telemetry overlay**, useful for observing vehicle dynamics during driving or model training.

</details>

---

<br><br><br>

### 🎥 Third-Person Camera View (` third_person_camera.py `)

<p align="center">
    <img src="raas_project/static/media/main_3rd.gif" alt="Third Person Camera Demo" width="800"/>
</p>

<p align="center"><em>⏳ The GIF may take a few seconds to load — please wait for the animation to appear</em></p>

#### ▶️ Launch Command
```
python third_person_camera.py
```

#### 🖥️ Example Console Output
```
[+] Vehicle found: vehicle.lincoln.mkz_2020 (ID 24)
[*] 3rd person camera is active. Press Q to exit.
```


This function activates an external camera placed behind the vehicle and streams live footage.  
It is used for **visual observation of the vehicle from the outside**, which is helpful when testing vehicle behavior, visual effects, or recording demos and simulation footage.

The camera maintains a stable rear-overhead angle, offering a full view of the environment around the car.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* A connection is established with the CARLA server, and ` world ` and ` blueprint_library ` objects are initialized.
* The script searches for all ` vehicle.lincoln.mkz_2020 ` actors and selects the one with the lowest ID. If none are found, execution is halted.
* An RGB camera (` sensor.camera.rgb `) is created with:
  - Resolution: 640×480;
  - Field of view: 90°.
* The camera is positioned behind the vehicle at:
  - Coordinates: ` x = -10, y = 0, z = 4 `, with a slight ` yaw = -1 ` for angle adjustment.
* The camera is spawned and attached to the vehicle using ` spawn_actor(..., attach_to=vehicle) `.
* Image streaming is started using `.listen()`. Each frame:
  - Is converted from ` raw_data ` into a NumPy array;
  - Extracts RGB values (alpha channel is discarded);
  - Is stored in the dictionary under ` image_data['back'] `.
* In the main loop:
  - If a new frame is available, it is displayed via ` cv2.imshow ` in a window titled `3rd person`;
  - The display updates at ~30 FPS;
  - The loop ends when the ` Q ` key is pressed.
* Upon exit:
  - The camera stream is stopped;
  - The camera actor is destroyed;
  - All OpenCV windows are closed (` cv2.destroyAllWindows()`).

This module provides a **simple third-person external view for visual vehicle tracking**, ideal for demos, trajectory visualization, and general simulation monitoring.

</details>

---

<br><br><br>

### 👁️ First-Person Camera View (` first_person_camera.py `)

<p align="center">
    <img src="raas_project/static/media/main_1st.gif" alt="First Person Camera Demo" width="800"/>
</p>

<p align="center"><em>⏳ The GIF may take a few seconds to load — please wait for the animation to appear</em></p>

#### ▶️ Launch Command
```
python first_person_camera.py
```


#### 🖥️ Example Console Output
```
[+] Vehicle found: vehicle.lincoln.mkz_2020 (ID 24)
[*] 1st person camera is active. Press Q to exit.
```


This function activates a camera positioned at the driver’s eye level and displays a real-time view.  
This mode is used for **visual road analysis from the driver’s perspective** and is essential for tasks such as dataset collection, perception testing, or model training.

The camera simulates the exact angle and viewpoint available to a person in a real car, including perspective, field of view, and height.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

- Connects to the CARLA server at ` localhost:2000 `, sets a 5-second timeout, and retrieves the active ` world ` and ` blueprint_library `.
- Filters all actors by the ` vehicle.lincoln.mkz_2020 ` blueprint. If a suitable vehicle is found, the first in the list is used.
- An RGB camera is configured with:
  - Resolution: 640×480;
  - Field of view: 110°;
  - Position: slightly offset from the driver’s head (` x=0.05, y=-0.35, z=1.2 `).
- The camera is spawned and attached to the vehicle using ` spawn_actor(..., attach_to=vehicle) `.
- Streaming is activated with `.listen()`, and each image is processed in the ` camera_callback `:
  - ` image.raw_data ` is converted into a NumPy array;
  - The image is formatted to RGB (alpha channel is discarded);
  - The result is saved in the ` image_data ` dictionary under the `'first'` key.
- In the main loop:
  - If a new frame is available, it is displayed via OpenCV (` cv2.imshow `) in a window titled `1st person`;
  - The window updates approximately every 30 ms.
- The script runs in real time until the user presses ` Q `.
- On exit:
  - The camera stream is stopped with `.stop()` and the actor is destroyed with `.destroy()`;
  - All OpenCV display windows are closed.

This script provides a **realistic in-cabin view**, especially useful for simulating driver perception, visual systems, and road interface testing.

</details>

---

<br><br><br><br><br>

---

# 🌍 Environment Simulation (` world_setup `)

---

## 🗺️ Scripts for World Generation, Traffic Management, and Object Control

This folder contains scripts and auxiliary files required for **creating, managing, and resetting the simulation environment**.  
It includes tools for traffic generation, vehicle spawning, route recording, and object control.

These files are essential for simulating road conditions, reproducing driving scenarios, and maintaining a clean simulation state.

### 📜 File Descriptions

- **` cleanup_traffic.py `**  
  Removes all active traffic from the simulation.

- **` destroy_all_vehicles.py `**  
  Deletes all spawned vehicles and objects.

- **` generate_traffic_with_events.py `**  
  Generates traffic with predefined behaviors and events.

- **` get_vehicle_coords.py `**  
  Retrieves the current coordinates of a vehicle.

- **` path1.json `**  
  JSON file containing a recorded driving path.

- **` path2.json `**  
  Another JSON file with a different driving route.

- **` record_controls.py `**  
  Records vehicle control inputs for later playback or analysis.

- **` spawn_vehicle.py `**  
  Spawns a single vehicle in the environment.

- **` spawn_vehicles_from_file.py `**  
  Spawns multiple vehicles using coordinates from a file.

- **` vehicle_coords.txt `**  
  A plain text file containing spawn coordinates for vehicles.


---

<br>

### 🚦 Traffic Generation with Event Simulation (` generate_traffic_with_events.py `)

<p align="center">
    <img src="raas_project/static/media/world_create_traffic.gif" alt="Traffic Generation Demo" width="800"/>
</p>

<p align="center"><em>⏳ The GIF may take a few seconds to load — please wait for the animation to appear</em></p>

#### ▶️ Launch Command
```
python generate_traffic_with_events.py
```

#### 🖥️ Example Console Output
```
[INFO] Successfully found spawn locations for 0 walkers (after 50 attempts).
[+] Spawned 30 vehicles and 0 walkers
```


This script creates a **dynamic urban environment** by automatically spawning random vehicle traffic and pedestrians throughout the CARLA simulation map.  
It's useful for testing the main vehicle’s behavior in heavy traffic, stress-testing ADAS responses, and simulating complex driving scenarios.

**This function is launched manually as part of scenario-based tests** and can be adapted for any vehicle types or traffic density.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* Command-line arguments are used to define parameters such as:
  * Number of vehicles and pedestrians;
  * Filters for selecting models (` vehicle.* `, ` walker.pedestrian.* `);
  * Vehicle generation type.

* The script connects to CARLA using ` carla.Client `, then:
  * Retrieves suitable blueprints for vehicles and pedestrians;
  * Generates spawn points for cars based on the current map;
  * Randomly selects vehicle models and colors.

* Vehicles:
  * Are spawned with the ` autopilot ` role;
  * Autopilot is enabled, and they begin navigating the roads.

* Pedestrians:
  * Are assigned different walking speeds;
  * Are spawned with associated AI controllers (` controller.ai.walker `);
  * Are assigned random destinations on the map.

* A log is displayed showing the number of actors spawned and attempts made to place them.

* The simulation continues in the background using ` world.wait_for_tick() ` until terminated manually (e.g., ` Ctrl+C `).

* Upon exit, all spawned actors are properly destroyed.

This module is ideal for **setting up rich, realistic test environments with live traffic**, and for conducting experiments involving vehicle interactions with external urban elements.

</details>

---

<br><br><br>

### 🚗 Vehicle Spawning from File Coordinates (` spawn_vehicles_from_file.py `)

<p align="center">
    <img src="raas_project/static/media/world_create_from_file.gif" alt="Spawn Vehicles from File Demo" width="800"/>
</p>

<p align="center"><em>⏳ The GIF may take a few seconds to load — please wait for the animation to appear</em></p>

#### ▶️ Launch Command
```
python spawn_vehicles_from_file.py
```

#### 🖥️ Example Console Output
```
[DEBUG] Found city section: Town04
[DEBUG] Processing line: x=280.43, y=-226.39, z=0.18, yaw=178.87
[DEBUG] Processing line: x=279.70, y=-223.31, z=0.19, yaw=-1.76
[DEBUG] Processing line: x=280.16, y=-220.12, z=0.20, yaw=178.95
[DEBUG] Processing line: x=280.19, y=-217.12, z=0.21, yaw=-0.50
[DEBUG] Processing line: x=280.27, y=-210.79, z=0.22, yaw=-1.43
[DEBUG] Processing line: x=280.24, y=-207.56, z=0.23, yaw=-1.19
[DEBUG] Processing line: x=280.00, y=-204.21, z=0.24, yaw=179.24
[DEBUG] Processing line: x=279.97, y=-201.20, z=0.25, yaw=178.89
[DEBUG] Processing line: x=279.85, y=-198.02, z=0.26, yaw=178.78
[DEBUG] Processing line: x=280.39, y=-194.85, z=0.27, yaw=0.77
[DEBUG] Processing line: x=280.18, y=-191.42, z=0.28, yaw=1.36
[DEBUG] Processing line: x=290.75, y=-226.51, z=0.16, yaw=178.88
[DEBUG] Processing line: x=290.84, y=-223.32, z=0.17, yaw=178.25
[DEBUG] Processing line: x=290.60, y=-220.32, z=0.18, yaw=179.14
[DEBUG] Processing line: x=290.55, y=-213.91, z=0.20, yaw=-1.61
[DEBUG] Processing line: x=290.10, y=-210.78, z=0.21, yaw=178.58
[DEBUG] Processing line: x=290.47, y=-204.27, z=0.23, yaw=179.55
[DEBUG] Processing line: x=290.26, y=-197.87, z=0.23, yaw=-1.42
[DEBUG] Processing line: x=290.52, y=-191.71, z=0.23, yaw=-179.34
[DEBUG] Processing line: x=290.58, y=-188.21, z=0.23, yaw=-1.62
[DEBUG] Available vehicle blueprints:
[DEBUG] Available vehicles: ['vehicle.audi.a2', 'vehicle.nissan.micra', 'vehicle.audi.tt', 'vehicle.mercedes.coupe_2020', 'vehicle.bmw.grandtourer', 'vehicle.harley-davidson.low_rider', 'vehicle.ford.ambulance', 'vehicle.micro.microlino', 'vehicle.carlamotors.firetruck', 'vehicle.carlamotors.carlacola', 'vehicle.ford.mustang', 'vehicle.chevrolet.impala', 'vehicle.lincoln.mkz_2020', 'vehicle.citroen.c3', 'vehicle.dodge.charger_police', 'vehicle.nissan.patrol', 'vehicle.jeep.wrangler_rubicon', 'vehicle.mini.cooper_s', 'vehicle.mercedes.coupe', 'vehicle.dodge.charger_2020', 'vehicle.ford.crown', 'vehicle.seat.leon', 'vehicle.toyota.prius', 'vehicle.yamaha.yzf', 'vehicle.kawasaki.ninja', 'vehicle.bh.crossbike', 'vehicle.mitsubishi.fusorosa', 'vehicle.tesla.model3', 'vehicle.gazelle.omafiets', 'vehicle.tesla.cybertruck', 'vehicle.diamondback.century', 'vehicle.mercedes.sprinter', 'vehicle.audi.etron', 'vehicle.volkswagen.t2', 'vehicle.lincoln.mkz_2017', 'vehicle.dodge.charger_police_2020', 'vehicle.vespa.zx125', 'vehicle.mini.cooper_s_2021', 'vehicle.nissan.patrol_2021', 'vehicle.volkswagen.t2_2021']
[+] Spawned: vehicle.audi.etron at Location(x=280.429993, y=-226.389999, z=0.680000)
[+] Spawned: vehicle.mercedes.sprinter at Location(x=279.700012, y=-223.309998, z=0.690000)
[+] Spawned: vehicle.audi.tt at Location(x=280.160004, y=-220.119995, z=0.700000)
[+] Spawned: vehicle.chevrolet.impala at Location(x=280.190002, y=-217.119995, z=0.710000)
[+] Spawned: vehicle.ford.mustang at Location(x=280.269989, y=-210.789993, z=0.720000)
[+] Spawned: vehicle.audi.etron at Location(x=280.239990, y=-207.559998, z=0.730000)
[+] Spawned: vehicle.audi.tt at Location(x=280.000000, y=-204.210007, z=0.740000)
[+] Spawned: vehicle.chevrolet.impala at Location(x=279.970001, y=-201.199997, z=0.750000)
[+] Spawned: vehicle.seat.leon at Location(x=279.850006, y=-198.020004, z=0.760000)
[+] Spawned: vehicle.bmw.grandtourer at Location(x=280.390015, y=-194.850006, z=0.770000)
[+] Spawned: vehicle.mercedes.coupe at Location(x=280.179993, y=-191.419998, z=0.780000)
[+] Spawned: vehicle.audi.etron at Location(x=290.750000, y=-226.509995, z=0.660000)
[+] Spawned: vehicle.toyota.prius at Location(x=290.839996, y=-223.320007, z=0.670000)
[+] Spawned: vehicle.audi.etron at Location(x=290.600006, y=-220.320007, z=0.680000)
[+] Spawned: vehicle.toyota.prius at Location(x=290.549988, y=-213.910004, z=0.700000)
[+] Spawned: vehicle.toyota.prius at Location(x=290.100006, y=-210.779999, z=0.710000)
[+] Spawned: vehicle.tesla.model3 at Location(x=290.470001, y=-204.270004, z=0.730000)
[+] Spawned: vehicle.bmw.grandtourer at Location(x=290.260010, y=-197.869995, z=0.730000)
[+] Spawned: vehicle.tesla.model3 at Location(x=290.519989, y=-191.710007, z=0.730000)
[+] Spawned: vehicle.nissan.micra at Location(x=290.579987, y=-188.210007, z=0.730000)
[i] Spawned 20 vehicles.
Press Ctrl+C to exit and remove vehicles.
```


This script enables **spawning vehicles** in the CARLA simulation **based on predefined coordinates** stored in a text file. It extracts coordinates for the current city, checks for allowed vehicle models, and spawns them at specified locations. A random color is also applied to each vehicle when supported.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* The script starts by connecting to the CARLA server using ` carla.Client ` and retrieving the current world with ` client.get_world() `.
* It loads vehicle coordinates from the ` vehicle_coords.txt ` file, filtering only entries that match the current map.
* It checks whether each vehicle blueprint exists in the library. Only models listed in ` ALLOWED_VEHICLES ` are eligible for spawning.
* If a vehicle supports the **color** attribute, a random color is selected from its available options.
* Successfully matched vehicles are spawned at the coordinates specified in the file.
* The script runs continuously until manually interrupted via **Ctrl+C**.
* Upon exit, all spawned vehicles are properly destroyed to clean up the simulation.

Use cases:
- Ideal for **creating test scenarios** with specific vehicle positions.
- Useful for **simulating traffic with predetermined vehicle types**, enabling customized interaction testing.
- Includes **city filtering** and **vehicle whitelist support** to fine-tune the testing environment.

</details>

---

<br><br><br>

### 🧹 Traffic Cleanup in Simulation (` cleanup_traffic.py `)

<p align="center">
    <img src="raas_project/static/media/world_delete_traffic.gif" alt="Traffic Cleanup Demo" width="800"/>
</p>

<p align="center"><em>⏳ The GIF may take a few seconds to load — please wait for the animation to appear</em></p>

#### ▶️ Launch Command
```
python cleanup_traffic.py
```

#### 🖥️ Example Console Output
```
[*] Saving main vehicle: vehicle.lincoln.mkz_2020 (ID: 24)
[!] Removing 30 traffic actors...
[+] Done.
```


This function is designed to **automatically clean the CARLA scene of all traffic** — both vehicles and pedestrians — while preserving the main testing vehicle.

This is especially useful when testing RAAS features in an isolated environment, where external traffic could interfere with debugging, visual recording, or experiment accuracy.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* Connects to the CARLA simulation via ` carla.Client ` at ` localhost:2000 `.
* Retrieves the current ` world ` and all actors using ` get_actors() `.
* Filters actors into:
  * ` vehicle.* ` — all vehicles;
  * ` walker.* ` — all pedestrians.
* Identifies and preserves **the main vehicle** (assumed to be the one with the lowest ID).
* All other vehicles and pedestrians are collected into a deletion list.
* Actors are destroyed in bulk using ` client.apply_batch([...]) ` with ` carla.command.DestroyActor() ` — allowing for fast and efficient cleanup.
* Upon completion, the console prints the number of removed actors or a message if no traffic was present.

</details>

---

<br><br><br>

### 🧨 Full Deletion of All Vehicles and Simulation Objects (` destroy_all_vehicles.py `)

<p align="center">
    <img src="raas_project/static/media/world_delete_all.gif" alt="Full Cleanup Demo" width="800"/>
</p>

<p align="center"><em>⏳ The GIF may take a few seconds to load — please wait for the animation to appear</em></p>

#### ▶️ Launch Command
```
python destroy_all_vehicles.py
```

#### 🖥️ Example Console Output
```
[*] Found 31 vehicles. Destroying...
[+] All vehicles destroyed.
```


This script is designed for **complete removal of all vehicles in the CARLA simulation**.  
It is used when the scene needs to be fully reset — for instance, before restarting experiments, preparing a clean environment, or resolving spawn/load errors.

> ❗️ This script deletes **all** ` vehicle.* ` actors, including the primary test vehicle. Use with caution.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* Establishes a connection to the CARLA server using ` carla.Client ` at ` localhost:2000 `.
* Retrieves the current ` world ` and collects all actors of type ` vehicle.* ` — meaning every vehicle in the simulation.
* If no vehicles are found, an appropriate message is printed and the script exits.
* Then:
  * Iterates over all found vehicles;
  * Calls ` destroy() ` on each one.
* After deletion, a summary message confirms that all vehicles have been removed.

This is a simple but powerful tool for manually managing the simulation state and **resetting the environment before new test runs**.

</details>

---

<br><br><br>

### 🚗 Vehicle Creation and Initialization in Simulation (` spawn_vehicle.py `)

#### ▶️ Launch Command
```
python spawn_vehicle.py
```

#### 🖥️ Example Console Output
```
[] Connecting to the Carla server...
[+] Vehicle spawned successfully: vehicle.lincoln.mkz_2020 (ID 24)
[] Vehicle is active. Press Ctrl+C to exit...
```


This script is responsible for **creating and initializing a vehicle** in the CARLA simulation. In this example, a **Lincoln MKZ 2020** is selected from the available vehicle blueprints and **spawned at a random location** on the map.

The vehicle remains active in the simulation until the user manually interrupts the process. This functionality is useful for **testing vehicle behavior** under different conditions or creating training environments.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* The script begins by connecting to the CARLA server via ` carla.Client ` and retrieving the current world using ` client.get_world() `.
* It then searches the ` blueprint_library ` for a vehicle named **Lincoln MKZ 2020**.
* If the vehicle is found, the first matching blueprint is selected. If it supports the **color** attribute, the color is set to `"50,50,50"` (dark gray).
* A random **spawn point** is selected from the available map locations via ` get_spawn_points() `, and the vehicle is spawned at that point using the selected blueprint.
* Upon successful spawn, the vehicle type and actor ID are printed.
* The script then keeps the vehicle active in the simulation until the user stops it manually via **Ctrl+C**.
* When the script ends, the vehicle is destroyed and a shutdown message is displayed.

This script provides a convenient way to **spawn a vehicle at random** and maintain it in the simulation for **testing, experimentation, or integration purposes**.

</details>

---

<br><br><br>

### 🗺️ Retrieve Current Coordinates of Active Vehicle (` get_vehicle_coords.py `)

#### ▶️ Launch Command
```
python get_vehicle_coords.py
```

#### 🖥️ Example Console Output
```
pygame 2.6.1 (SDL 2.28.4, Python 3.7.0)
Hello from the pygame community. https://www.pygame.org/contribute.html
[+] Connected to vehicle: vehicle.lincoln.mkz_2020
[i] Use 'C' to save current location to vehicle_coords.txt
[+] Saved: x=412.72, y=-95.35, z=-0.01, yaw=-89.40
```


This function allows you to **retrieve the current coordinates of the active vehicle** in the CARLA simulation.  
It records the exact **(x, y, z)** position and **yaw (rotation)** of the vehicle into the ` vehicle_coords.txt ` file.  
This is especially useful for **debugging** or **tracking the vehicle’s position** during simulation.

**Activated by pressing the ` C ` key**, the script writes the current location to a text file for precise spatial logging.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* The script connects to the CARLA server using ` carla.Client ` and retrieves the active world using ` client.get_world() `.
* It fetches the first available vehicle actor:
  - If a vehicle is found, tracking begins;
  - If no vehicle is found, an appropriate message is shown.
* During runtime, on every frame:
  - The vehicle's coordinates and yaw angle are monitored;
  - When the ` C ` key is pressed, the current values are written to ` vehicle_coords.txt ` in the format:
    ```plaintext
    x=xxx.xx, y=xxx.xx, z=xxx.xx, yaw=xxx.xx
    ```
  - A 0.3-second delay is enforced to prevent duplicate entries from long key presses.
* Upon exiting or interrupting the simulation, the ` pygame ` window closes properly and the script terminates.

---

</details>

---

<br><br><br>

### 🎥 Logging Vehicle Movement and Control Snapshots for Analysis (` record_controls.py `)

#### ▶️ Launch Command
```
python record_controls.py
```

#### 🖥️ Example Console Output
```
pygame 2.6.1 (SDL 2.28.4, Python 3.7.0)
Hello from the pygame community. https://www.pygame.org/contribute.html
[+] Using vehicle: vehicle.lincoln.mkz_2020 (id=225)
```


This script allows you to **record vehicle movement data**, including **coordinates**, **rotation angles**, and **control inputs** (steering, throttle, brake, gear states), and save them in a **JSON file**.  
It is useful for **post-simulation analysis**, modeling vehicle behavior in different scenarios, and testing system responses.

**It starts manually and logs movement continuously** while the vehicle is active in the scene, also displaying current control parameters and position on screen.

#### 📜 More About Script Operation

<details>
<summary>📜 More About Script Operation</summary>

* The script connects to the CARLA server via ` carla.Client ` and gets the current world using ` client.get_world() `.
* It fetches the first available vehicle actor:
  - If found, it starts tracking the vehicle's location and control states;
  - If no vehicle is found, an error message is shown.
* During each frame:
  - It collects current vehicle coordinates, rotation angles, and control parameters (steer, throttle, brake, gear, etc.);
  - The data is stored in a list called ` recorded_path ` which logs all movement and control states.
* The script also allows toggling **manual gear mode**. When enabled, gears can be switched using keys ` R ` to ` 6 `.
* All logged information is saved in a file named ` path.json ` in the following format:
  ```json
  [
    {
      "timestamp": 0.1,
      "x": 10.5,
      "y": -5.3,
      "z": 1.2,
      "yaw": 30.5,
      "pitch": 0.0,
      "roll": 0.0,
      "steer": 0.1,
      "throttle": 1.0,
      "brake": 0.0,
      "reverse": false,
      "gear": 1,
      "manual_gear": false,
      "hand_brake": false
    },
    ...
  ]
  ```
The screen displays current vehicle position, rotation, and control status in real time.

The program continues logging until it is manually terminated with QUIT or Ctrl+C.

🗂️ What’s Logged in path.json?

Each movement entry includes:

- timestamp — simulation time at the moment of logging;

- x, y, z — spatial coordinates of the vehicle;

- yaw, pitch, roll — orientation angles;

- steer — steering input;

- throttle, brake — throttle and braking values;

- reverse — whether reverse gear is engaged;

- gear — current gear;

- manual_gear — if manual gear mode is active;

- hand_brake — handbrake status.

This data is essential for analyzing vehicle behavior, validating system reactions, and performing reproducible scenario testing.

</details> 

---

<br><br><br><br><br>

---


# 🖼️ Media Files (` static `)

---

<br>

## 🖼️ Images, GIFs, and Videos Used in the Driver Assistance System

This folder contains **all multimedia resources** used or prepared for integration into the system.  
It includes UI illustrations, visual elements, animations, archive materials, and documentation graphics.

The content is organized into subfolders based on its purpose and area of use.

### 📁 Folder Overview

- **` media/ `**  
  Contains all visual assets used in ` README.md ` files and other documentation across the project.  
  Includes GIFs, screenshots, and diagrams demonstrating system functionality, project structure, and UI.  
  These files provide **visual representation for the GitHub repository**.

- **` photos/ `**  
  Contains images and GIFs **actively used** by the system itself.  
  These resources are embedded in the interface and support information display or visual feedback.

- **` source/ `**  
  Contains **additional media files** — images and videos.  
  These are resources considered for use but ultimately excluded due to format, duplication, or redundancy.  
  This folder acts as a **resource archive** for potential future use.

---

<br><br><br><br><br>

---

# 📄 Documentation (` docs `)

---

<br>

## 📑 Reports, System Analysis, and Supporting Materials

This folder is the central repository for **all documentation related to the project**, explaining system architecture, development process, and design choices.  
It contains technical reports, explanatory notes, system analysis, and modeling artifacts.

These documents are essential for:
- Understanding the structure and logic of the system  
- Justifying architectural and design decisions  
- Presenting the project in an academic or technical context

---

<br><br><br><br><br>

---

# ⚙️ Development Environment & Dependencies

---

<br>

## Hardware Configuration Used During Development:
- **Operating System**: Windows 10 Pro 64-bit  
- **Graphics Card**: GTX 960 4GB  
- **RAM**: 16 GB  
- **CPU**: Intel Core i5-4460

## Primary Python Libraries Used:

Below is the **complete list of Python libraries** used in the project with pinned versions:

```
carla==0.9.14
certifi==2025.4.26
charset-normalizer==3.4.1
cycler==0.11.0
fonttools==4.38.0
idna==3.10
kiwisolver==1.4.5
matplotlib==3.5.1
numpy==1.21.6
opencv-python==4.11.0.86
packaging==24.0
Pillow==9.5.0
pygame==2.6.1
pyparsing==3.1.4
PyQt5==5.15.4
PyQt5-Qt5==5.15.2
PyQt5-sip==12.8.1
python-dateutil==2.9.0.post0
requests==2.31.0
six==1.17.0
torch @ https://download.pytorch.org/whl/cu111/torch-1.10.2%2Bcu111-cp37-cp37m-win_amd64.whl
torchaudio @ https://download.pytorch.org/whl/cu111/torchaudio-0.10.2%2Bcu111-cp37-cp37m-win_amd64.whl
torchvision==0.11.3
typing_extensions==4.7.1
urllib3==1.26.15
```

> ⚠️ Some libraries are installed from external sources (` torch `, ` torchaudio `) — make sure to use the correct CUDA 11.1-compatible versions if running on GPU.

---

<br><br><br><br><br>

---

# 🙏 Acknowledgements

---

<br>

## 🙌 I would like to thank the authors of the following projects:

During the development of this system, I studied various open-source solutions that helped me understand how to work with the CARLA simulator and inspired the implementation of certain components:

- [Aravindseenu / carla](https://github.com/Aravindseenu/carla)  
- [vignif / carla-parking](https://github.com/vignif/carla-parking)  
- [qintonguav / e2e-parking-carla](https://github.com/qintonguav/e2e-parking-carla)  
- [Sentdex / Carla-RL](https://github.com/Sentdex/Carla-RL)  
- [angelkim88 / CARLA-Lane_Detection](https://github.com/angelkim88/CARLA-Lane_Detection)  
- [kochlisGit / Autonomous-Vehicles-Adaptive-Cruise-Control](https://github.com/kochlisGit/Autonomous-Vehicles-Adaptive-Cruise-Control)  
- [Jasa22 / carla_cruise_control](https://github.com/Jasa22/carla_cruise_control)  
- [DeepakSingh260 / Carla](https://github.com/DeepakSingh260/Carla)  
- [SCP-CN-001 / carla_autopilot](https://github.com/SCP-CN-001/carla_autopilot)

---

