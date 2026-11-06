from PyQt5 import QtWidgets, QtCore
from utils import MotorDriver_utils, IMU_utils
import sys

app = QtWidgets.QApplication(sys.argv)

# =========================================================
# RFC Main Window
# =========================================================
MotorDriver = QtWidgets.QMainWindow()
ui = MotorDriver_utils.UI_MotorDriver()
ui.setupUi(MotorDriver)
MotorDriver.show()

# =========================================================
# IMU Window
# =========================================================
IMUWindow = QtWidgets.QMainWindow()
imu = IMU_utils.UI_IMUWindow()
imu.setupIMU_UI(IMUWindow)

IMUWindow.show()
sys.exit(app.exec_())
