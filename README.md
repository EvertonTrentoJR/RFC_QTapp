# RockFlow cell Application control

**PyQt app to control step-motor RFC — Powered by LASII**

---

# 0. Table of Contents

1. [Repository Structure](#1-repository-structure)
2. [Methodology](#2-methodology)
3. [Dataset](#3-dataset)
4. [Getting Started](#4-getting-started)
5. [Dependencies](#5-dependencies)
6. [Contributors](#6-contributors)

---

# 1. Repository Structure

```text
RFC_QTapp/
│
├── utils/
│   ├── stylesheet.qss
│   ├── MainWindow_utils.py
├── RFCControl_main.py
├── requirements.txt
└── .gitignore
```

## Folder Description

| Folder/File | Description                                  |
|---|----------------------------------------------|
| `utils/` | Core utility functions and framework modules |
| `utils/stylesheet.qss` | Stylesheet for the QT application |
| `utils/MainWindow_utils.py` | Core utility functions for the Main Window |
| `RFCControl_main.py` | Main script for impedance fitting workflow   |
| `requirements.txt` | Python dependencies required for the project |

---

# 2. Methodology


## Main Features

---

# 3. Getting Started

## Clone the repository

```bash
git clone https://github.com/your_username/RFC_QTapp.git
cd RFC_QTapp
```

## Python Version

> **⚠️ This project requires Python 3.11.x.**

The application has been tested with **Python 3.11**. Newer versions (e.g., Python 3.13) are **not supported** due to compatibility issues with **PyQt5** and **pyqt5-tools**.

## Installation

Create a virtual environment using Python 3.11:

```bash
py -3.11 -m venv .venv
```

Activate the environment:

**Windows (PowerShell)**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt)**

```cmd
.venv\Scripts\activate.bat
```

Install the dependencies:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

# 5. Dependencies

The following libraries are required to run this project:

```python
PyQt5         # graphical user interface (GUI) framework
pyqt5-tools   # Qt Designer and development tools
numpy         # numerical computing
scipy         # scientific computing and optimization
pandas        # data manipulation and analysis
matplotlib    # data visualization
```
---

# 6. Contributors

- @EvertonTrentoJR

