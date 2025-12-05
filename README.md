# Lower-Extremity Guided and Assisted Rehabilitation Device (LEGARD) 

## Overview 🦵

The LEGARD (Lower-Extremity Guided and Assisted Rehabilitation Device) is an innovative rehabilitation tool designed to aid in post-surgical hip rehabilitation by improving hip strength and range of motion. Developed by a collaborative team of UNM physical therapy students, engineering students, and recent graduates, the LEGARD project aims to provide an effective in-home alternative to traditional rehabilitative care.

---

### Project Motivation 💡

Due to barriers in accessing adequate post-surgical rehabilitative care, particularly for in-home settings, LEGARD was conceptualized and designed as a potential in-home rehabilitation device. In-home rehab care is becoming increasingly relevant, and innovations like LEGARD seek to make this experience more accessible and effective for patients.

### Prototype Development 🏗️

This prototype is a collaboration between physical therapy and engineering disciplines, co-sponsored by the University of New Mexico's College of Engineering (COE) and UNM Rainforest Innovations. The device was showcased at a UNM event, highlighting advancements in orthopedic rehabilitation practices.

---

## Technical Architecture 💻

The LEGARD application is built using a modular Python structure with **Tkinter** for the graphical user interface and multithreading for concurrent hardware and data management.

### Key Components 🧩

* **`core.auth_manager` (Authentication):**
    * Handles user **registration** and **login** using usernames and 4-digit PINs.
    * Securely stores user credentials (hashed PINs) and profile data (first name, last name, gender) in a local CSV file (`users.csv`).
    * **Uses SHA256 hashing with a salt** for PIN security.

* **`core.config_manager` (Configuration):**
    * Manages application settings by reading and writing to the `config.ini` file.
    * Handles settings for **Serial Communication**, **Plotting limits**, and **Repetition Counter Algorithm parameters**.

* **`core.data_inputs` (Hardware Threading):**
    * **`SerialThread`:** Manages asynchronous, line-based communication with a serial device (e.g., a balance board), ensuring the GUI remains responsive while waiting for data.
    * **`SensorThread`:** Continuously polls the **BNO055 IMU sensor** (via I2C) to fetch quaternion data for angle calculation in a dedicated, non-blocking thread.

* **`ui.auth_ui` (Authentication UI):**
    * Presents the **LoginApp** (main screen) and **RegistrationWindow** (Toplevel), handling user input validation for the authentication process.

* **`ui.dashboard` (Main Application Hub):**
    * The central window of the application, featuring a `ttk.Notebook` with multiple tabs (Profile, Routine, History, Analytics, Settings).
    * Initializes and manages the lifespan of the `SerialThread` and `SensorThread`.

---

## Application Workflow and Features ✨

### 1. User Authentication 🔒
The application starts with the `LoginApp`. New users can register, providing a unique username and a 4-digit PIN.

### 2. Routine and Calibration 📐
* **`ui.windows.calibration_window`:** Guides the user through a two-step process:
    1.  **Zeroing:** Establishes a baseline `initial_angle` by averaging sensor readings while the user stands still.
    2.  **Max Angle Tracking:** Determines the user's safe **Maximum Range of Motion (`max_angle`)** by tracking the highest angle achieved during a guided movement.
* **`ui.windows.routine_window`:**
    * Launches after successful calibration.
    * Hosts the **`DataProcessor`** thread, which performs **real-time data processing** (smoothing, velocity calculation, rep counting) and CSV logging.
    * Features **live, scrolling Matplotlib plots** for **Center of Pressure (CoP)** and **Relative Angle**.
    * Implements a **Repetition Counting Algorithm** that uses velocity and angle thresholds to detect successful repetitions.
    * Manages multi-set routines, including optional **Rest Timer** pop-ups between sets.

### 3. Data Analysis and Management 📊

* **`ui.tabs.history_tab`:** Allows the user to select any previous session and set to view the raw data. Features an interactive plot scrubber to synchronize the **Center of Pressure (CoP)** plot and **Relative Angle** plot across time.
* **`ui.tabs.analytics_tab`:** Reads logged session data from CSV files and provides **data visualizations** using Matplotlib. Graphs include:
    * Repetitions per Day
    * Sessions per Week
    * Average Velocity per Session
    * Average Max Angle per Session
* **`ui.tabs.settings_tab`:** Provides a GUI to adjust critical application parameters defined in `config.ini`, including:
    * Serial Port / Baudrate
    * Repetition Counter Tuning (Smoothing Window, Velocity Thresholds, Target Angle Tolerance)
    * Plotting Time Window
    * Includes a feature to open the user's session log folder.

---

## 🛠️ Project Setup and Dependencies

### 1. Python Application Dependencies (`requirements.txt`)

The main GUI application requires the following non-standard Python libraries. It is highly recommended to install these within a virtual environment (`pip install -r requirements.txt`).

| Package | Purpose |
| :--- | :--- |
| **`pyserial`** | Handles communication with the Arduino serial device. |
| **`matplotlib`** | Used for all live and historical data visualization (plotting). |
| **`numpy`** | Provides high-performance array operations for data processing. |
| **`adafruit-blinka`** | Enables the use of CircuitPython libraries (like the BNO055 driver) on Linux/SBCs. |
| **`adafruit-circuitpython-bno055`** | Driver for the BNO055 9-DOF IMU sensor. |

### 2. 🤖 Embedded System Firmware (Arduino Controller)

The application relies on a custom firmware running on an Arduino Nano to handle the four-scale Center of Pressure (CoP) platform.

#### 2.1. Hardware:
* **1 x Arduino Nano** (or compatible board)
* **4 x Strain Gauge Load Cells** and **4 x HX711 Amplifier Modules**.

#### 2.2. Firmware Source:
The custom firmware files (e.g., `cop_controller.ino`, `Scale.h`, etc.) must be compiled and uploaded to the Arduino Nano.

#### 2.3. Software Dependencies (Arduino Libraries):
The following library must be installed in the Arduino IDE via the **Library Manager** before compiling the firmware:

* **`HX711`** (by Bogdan Necula and Andreas Motl).

---

## ⚙️ Configuration (`config.ini`)

The core behavior of the application is controlled by the following default settings:

| Section | Parameter | Default Value | Description |
| :--- | :--- | :--- | :--- |
| **[Serial]** | `baudrate` | 115200 | Communication speed with the hardware device. |
| **[RepCounter]** | `smoothing_window` | 7 | Number of data points for moving average smoothing on angle data. |
| | `velocity_pos_threshold` | 10.0 | Min positive velocity (degrees/sec) to register the *start* of a rep. |
| | `velocity_neg_threshold` | -10.0 | Min negative velocity (degrees/sec) to register the *return* movement. |
| | `max_angle_tolerance_percent` | 50.0 | Percentage of the calibrated max angle required to count a successful rep. |
| **[Plotting]** | `time_window_seconds` | 5 | Time window (in seconds) for the live angle plot. |
| | `cop_x_limit`, `cop_y_limit` | 1.0 | X and Y axis limits for the Center of Pressure plot (cm). |