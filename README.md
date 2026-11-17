# RFC Motor Control & IMU Monitor

**A PyQt5 desktop application for controlling a stepper motor and monitoring an inertial measurement unit (IMU) in a Rock-Flow Cell (RFC) experimental setup.**

Developed for experimental instrumentation at **LASII**.

[Releases](https://github.com/EvertonTrentoJR/RFC_QTapp/releases) · [Source code](https://github.com/EvertonTrentoJR/RFC_QTapp)

> **Project status:** Laboratory/research software. Confirm hardware compatibility and test safety controls before operating the motor. The GUI and serial connections do not replace independent motor safety measures.

## Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Repository structure](#repository-structure)
4. [Requirements](#requirements)
5. [Installation and usage](#installation-and-usage)
6. [Serial connections](#serial-connections)
7. [Building the Windows executable](#building-the-windows-executable)
8. [Troubleshooting](#troubleshooting)
9. [Releases and repository files](#releases-and-repository-files)
10. [Contributors](#contributors)

## Overview

The RFC control application provides two **separate graphical windows**:

- **Motor Control:** operates a stepper motor through an Arduino-based motor controller.
- **IMU Monitor:** reads measurements from a BNO085-based acquisition system and displays the measured **pitch** in a PyVista 3D view.

The main launcher (`RFCControl_main.py`) starts each window in a **separate Python process**, giving each its own Qt event loop and serial-port connection. This isolates the interfaces at the software-process level; it does **not** eliminate electrical noise, USB faults, or sensor-bus problems.

```text
                  RFCControl_main.py
                        │
           ┌────────────┴────────────┐
           │                         │
     Motor GUI process          IMU GUI process
       (PyQt5)                    (PyQt5)
           │                         │
    Serial / Arduino          Serial / IMU MCU
       (e.g. COM3)              (e.g. COM5/COM8)
           │                         │
      Motor driver             BNO085 sensor
                                  │
                          PyVista pitch view
```

## Features

### Motor control

- Configure angular displacement, speed, acceleration, repetitions, and movement timing.
- Select motion, angle, and home operations.
- Send commands over a configurable serial port.
- Monitor serial responses and save supported experimental data to CSV.

### IMU monitoring

- Display acceleration, angular velocity, magnetic field, and quaternion components.
- Visualize **pitch-only** orientation of the experimental component in 3D using PyVista/PyVistaQt.
- Select a serial port and baud rate independently from the motor GUI.
- Save IMU measurements to CSV.
- Inspect serial messages and diagnostics when troubleshooting acquisition.

### Application architecture

- Two independently launched PyQt5 windows/processes.
- Separate serial connections for motor and IMU hardware.
- Individual startup modes for debugging either interface.

## Repository structure

```text
RFC_QTapp/
├── RFCControl_main.py           # Launcher for both GUI processes
├── utils/
│   ├── __init__.py              # Package initializer
│   ├── MotorDriver_utils.py     # Motor-control GUI and serial logic
│   ├── IMU_utils.py             # IMU GUI, acquisition, and 3D visualization
│   └── stylesheet.qss           # Shared Qt stylesheet
├── requirements.txt            # Python dependencies, if present
├── RFC_driver_IMU_icon.ico     # Optional custom executable icon
├── .gitignore
└── README.md
```

> The icon and `requirements.txt` are shown as project assets to include as applicable. The application itself depends on the three files under `utils/` plus the launcher and stylesheet.

## Requirements

- **Windows 10/11** for the provided PowerShell commands and Windows `.exe` build.
- **Python 3.11** (the version used in the documented development/build environment).
- Compatible motor-control firmware and IMU acquisition firmware communicating over serial ports.

Main Python dependencies:

| Package | Purpose |
|---|---|
| `PyQt5` | Graphical interfaces and Qt event loops |
| `pyserial` | USB/serial communication |
| `numpy` | Numerical operations and quaternion calculations |
| `pyvista` | 3D geometry and visualization |
| `pyvistaqt` | Embedding VTK/PyVista inside the Qt GUI |
| `pyinstaller` | Building a standalone Windows executable (optional) |

`pyqt5-tools` may be useful during GUI design but is not required solely to run the application.

## Installation and usage

### Option A — Download a Windows release

Download the Windows executable from [GitHub Releases](https://github.com/EvertonTrentoJR/RFC_QTapp/releases) **when a release asset is available**. Use a build tested for your hardware and Windows configuration.

The executable does not require a separate Python installation. Windows USB/serial drivers and the connected hardware are still required.

### Option B — Run from source

Clone the repository:

```powershell
git clone https://github.com/EvertonTrentoJR/RFC_QTapp.git
cd RFC_QTapp
```

Create and activate a Python 3.11 environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Install dependencies if `requirements.txt` is included:

```powershell
python -m pip install -r requirements.txt
```

Alternatively, install the runtime dependencies directly:

```powershell
python -m pip install PyQt5 pyserial numpy pyvista pyvistaqt
```

Launch **both** windows:

```powershell
python RFCControl_main.py
```

Launch just the motor window:

```powershell
python RFCControl_main.py --motor
```

Launch just the IMU window:

```powershell
python RFCControl_main.py --imu
```

After the windows open, select the appropriate COM port in **each** GUI and click its connect control. Opening a window does not automatically establish a hardware connection.

## Serial connections

| Interface | Hardware | Example port | GUI default baud rate |
|---|---|---|---|
| Motor Control | Arduino UNO R4 / compatible motor controller | `COM3` | `2000000` |
| IMU Monitor | Microcontroller reading a BNO085 | `COM5` or `COM8` | `115200` |

**COM numbers are examples only.** Check Windows Device Manager to identify the correct port. Close other programs using that port before connecting.

The IMU reader expects a comma-separated line of **13 numeric fields** in this order:

```text
Ax,Ay,Az,Gx,Gy,Gz,Mx,My,Mz,Qi,Qj,Qk,Qr
```

The 3D visualization intentionally uses **pitch only**; roll and yaw are not applied to the displayed model.

## Building the Windows executable

Install PyInstaller in the virtual environment:

```powershell
python -m pip install pyinstaller
```

From the project root, create a diagnostic build **with a visible console**:

```powershell
pyinstaller --clean --noconfirm --onefile --console `
  --name StepperMotorControl `
  --add-data "utils/stylesheet.qss;utils" `
  RFCControl_main.py
```

Once both windows have been tested successfully, build the windowed version with the optional custom icon:

```powershell
pyinstaller --clean --noconfirm --onefile --windowed `
  --name StepperMotorControl `
  --icon "RFC_driver_IMU_icon.ico" `
  --add-data "utils/stylesheet.qss;utils" `
  RFCControl_main.py
```

The output is placed in `dist/StepperMotorControl.exe`.

**Important for packaged builds:** When frozen, `sys.executable` points to `StepperMotorControl.exe`, **not** `python.exe`. The launcher must spawn itself with `--motor` or `--imu` and must not pass a Python script path or interpreter-only flags (such as `-u`). Use the frozen-aware version of `RFCControl_main.py` when packaging.

The `--icon` option embeds an icon into the `.exe`. Showing that same icon inside the PyQt windows requires separate runtime `QIcon` setup and bundling the icon as data.

## Troubleshooting

### An `.exe` does not open

First build with `--console` instead of `--windowed`, then run the executable from PowerShell:

```powershell
.\dist\StepperMotorControl.exe --motor
.\dist\StepperMotorControl.exe --imu
```

Check any reported Python import, Qt plugin, or VTK/OpenGL error. A successful PyInstaller build does **not** confirm that the application runs correctly.

### IMU values do not update

- Confirm the correct COM port and `115200` baud rate in the IMU window.
- Test the IMU window alone: `python RFCControl_main.py --imu`.
- Check whether serial packets contain 13 numeric fields and whether the quaternion changes when the sensor is moved.
- An increasing valid-packet counter does **not**, by itself, prove that new sensor measurements are being generated.

### IMU freezes when motor power is enabled

If the issue occurs specifically when the motor supply or driver is energized, investigate electrical interference, grounding, power integrity, USB cabling, and the IMU-to-microcontroller interface. Process isolation cannot correct a physical communication problem.

**Electrical safety:** Do not bypass protective earth or modify energized mains wiring. Use qualified personnel for inspections involving the 220 V power system.

## Releases and repository files

Compiled Windows executables may exceed GitHub's **100 MB per-file limit for ordinary Git repository objects**. Do not commit the PyInstaller executable or build output to the repository.

Suggested `.gitignore` entries:

```gitignore
.venv/
__pycache__/
*.py[cod]
.idea/
build/
dist/
*.exe
```

Publish the compiled `.exe` as a downloadable asset in [GitHub Releases](https://github.com/EvertonTrentoJR/RFC_QTapp/releases), while keeping Python source files, documentation, and the stylesheet in Git.

If a large executable was previously committed, removing it from the working directory or adding `.gitignore` is not enough: the oversized file must also be absent from the **unpushed Git history** being sent to GitHub.

## Contributors

- [@EvertonTrentoJR](https://github.com/EvertonTrentoJR)

**LASII — experimental instrumentation and RFC development.**
