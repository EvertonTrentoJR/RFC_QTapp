"""Launch the RFC motor controller and BNO085 IMU as separate Qt processes.

Usage:
    python RFCControl_main.py           # start both independent GUI processes
    python RFCControl_main.py --motor   # start only the motor GUI (for debugging)
    python RFCControl_main.py --imu     # start only the IMU GUI (for debugging)

Expected project layout:
    RFCControl_main.py
    utils/
        __init__.py
        MotorDriver_utils.py
        IMU_utils.py
        stylesheet.qss
"""

import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def run_window(mode: str) -> int:
    """Run exactly one QApplication in this child Python process."""
    from PyQt5 import QtWidgets

    # Do not pass our private --motor/--imu flags to Qt.
    app = QtWidgets.QApplication([sys.argv[0]])
    window = QtWidgets.QMainWindow()

    if mode == "motor":
        from utils import MotorDriver_utils

        ui = MotorDriver_utils.UI_MotorDriver()
        ui.setupUi(window)
    elif mode == "imu":
        from utils import IMU_utils

        ui = IMU_utils.UI_IMUWindow()
        ui.setupIMU_UI(window)
    else:
        raise ValueError(f"Unknown window: {mode}")

    # Keep the Python controller object alive for the lifetime of the window.
    window.ui = ui
    window.show()
    return app.exec_()


def launch_process(mode: str) -> subprocess.Popen:
    """Start a second Python interpreter, isolated from the other GUI."""
    return subprocess.Popen(
        [sys.executable, "-u", str(Path(__file__).resolve()), f"--{mode}"],
        cwd=str(BASE_DIR),
    )


def stop_processes(processes: dict) -> None:
    """Best-effort shutdown if the launcher is interrupted."""
    for process in processes.values():
        if process.poll() is None:
            process.terminate()

    for process in processes.values():
        if process.poll() is None:
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def main() -> int:
    if len(sys.argv) == 2:
        if sys.argv[1] == "--motor":
            return run_window("motor")
        if sys.argv[1] == "--imu":
            return run_window("imu")
        print(f"Unknown option: {sys.argv[1]}", file=sys.stderr)
        return 2

    if len(sys.argv) != 1:
        print("Usage: python RFCControl_main.py [--motor | --imu]", file=sys.stderr)
        return 2

    processes = {}
    try:
        processes["motor"] = launch_process("motor")
        processes["imu"] = launch_process("imu")
        print("RFC applications launched in separate processes:", flush=True)
        for name, process in processes.items():
            print(f"  {name.upper():5} PID={process.pid}", flush=True)

        reported = set()
        while len(reported) < len(processes):
            for name, process in processes.items():
                code = process.poll()
                if code is not None and name not in reported:
                    print(f"{name.upper()} window exited (code {code}).", flush=True)
                    reported.add(name)
            if len(reported) < len(processes):
                time.sleep(0.2)

        return 0
    except KeyboardInterrupt:
        print("\nLauncher interrupted; stopping child processes.", flush=True)
        stop_processes(processes)
        return 130
    except Exception:
        stop_processes(processes)
        raise


if __name__ == "__main__":
    sys.exit(main())