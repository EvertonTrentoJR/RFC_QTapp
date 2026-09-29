from PyQt5 import QtWidgets, QtCore
from utils import MainWindow_utils, IMU_utils
import sys

app = QtWidgets.QApplication(sys.argv)

# =========================================================
# RFC Main Window
# =========================================================
MainWindow = QtWidgets.QMainWindow()
ui = MainWindow_utils.UI_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()

# =========================================================
# IMU Window
# =========================================================
IMUWindow = QtWidgets.QMainWindow()
imu = IMU_utils.UI_IMUWindow()
imu.setupIMU_UI(IMUWindow)

IMUWindow.show()
# =========================================================
# DEBUG: GUI heartbeat
# =========================================================

heartbeat = QtCore.QTimer()

heartbeat.timeout.connect(
    lambda: print("[GUI] alive")
)

heartbeat.start(1000)


sys.exit(app.exec_())


sys.exit(app.exec_())