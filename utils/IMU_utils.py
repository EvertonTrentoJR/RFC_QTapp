# import relevant packages
from PyQt5 import QtCore, QtGui, QtWidgets
from pathlib import Path
from serial import Serial, SerialException
from serial.tools import list_ports
import time
import numpy as np
import pyvista as pv
import pyvistaqt as pvqt

# Load the stylesheet once when this module is imported
_STYLE_PATH = Path(__file__).parent / "stylesheet.qss"

with open(_STYLE_PATH, "r", encoding="utf-8") as f:
    STYLEsheet = f.read()


class UI_IMUWindow(object):

    def setupIMU_UI(self, IMUWindow):

        self.IMUWindow = IMUWindow

        IMUWindow.setObjectName("IMUWindow")
        IMUWindow.resize(700, 500)
        IMUWindow.setStyleSheet(STYLEsheet)
        IMUWindow.setWindowTitle("IMU Serial Monitor")

        self.thread = None
        self.worker = None

        # Central Widget
        self.centralWidget = QtWidgets.QWidget(IMUWindow)
        self.centralWidget.setObjectName("centralWidget")
        IMUWindow.setCentralWidget(self.centralWidget)

        self.centralLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.centralLayout.setContentsMargins(10, 10, 10, 5)
        self.centralLayout.setSpacing(5)

        # Main Layout
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setSpacing(10)

        self.centralLayout.addLayout(self.mainLayout, 1)

        # =========================================================
        # IMU Sidebar
        # =========================================================

        self.frameIMU = QtWidgets.QFrame(self.centralWidget)
        self.frameIMU.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameIMU.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameIMU.setObjectName("frameIMU")
        self.frameIMU.setMinimumWidth(240)
        self.frameIMU.setMaximumWidth(240)

        self.imuLayout = QtWidgets.QVBoxLayout(self.frameIMU)
        self.imuLayout.setContentsMargins(3, 3, 3, 3)
        self.imuLayout.setSpacing(6)

        # IMU Serial Connection
        self.labelIMUTitle = QtWidgets.QLabel(self.frameIMU)
        self.labelIMUTitle.setObjectName("labelIMUTitle")
        self.labelIMUTitle.setText("IMU Serial Connection")
        self.imuLayout.addWidget(self.labelIMUTitle)

        # Serial Port
        self.portLayout = QtWidgets.QHBoxLayout()
        self.labelSerialPort = QtWidgets.QLabel(self.frameIMU)
        self.labelSerialPort.setText("Port:")
        self.comboSerialPort = QtWidgets.QComboBox(self.frameIMU)
        self.comboSerialPort.setObjectName("comboSerialPort")
        self.btnRefreshPorts = QtWidgets.QPushButton(self.frameIMU)
        self.btnRefreshPorts.setObjectName("btnRefreshPorts")
        self.btnRefreshPorts.setText("↻")
        self.btnRefreshPorts.setFixedSize(35, 35)
        self.portLayout.addWidget(self.labelSerialPort)
        self.portLayout.addWidget(self.comboSerialPort)
        self.portLayout.addWidget(self.btnRefreshPorts)
        self.imuLayout.addLayout(self.portLayout)

        # Baud Rate
        self.baudLayout = QtWidgets.QHBoxLayout()
        self.labelBaudrate = QtWidgets.QLabel(self.frameIMU)
        self.labelBaudrate.setText("Baud:")
        self.lineBaudrate = QtWidgets.QLineEdit(self.frameIMU)
        self.lineBaudrate.setObjectName("lineBaudrate")
        self.lineBaudrate.setText("115200")
        self.baudLayout.addWidget(self.labelBaudrate)
        self.baudLayout.addWidget(self.lineBaudrate)
        self.imuLayout.addLayout(self.baudLayout)

        # Connect
        self.btnConnect = QtWidgets.QPushButton(self.frameIMU)
        self.btnConnect.setObjectName("btnConnect")
        self.btnConnect.setText("CONNECT")
        self.imuLayout.addWidget(self.btnConnect)

        # Divider
        self.line1 = QtWidgets.QFrame(self.frameIMU)
        self.line1.setFrameShape(QtWidgets.QFrame.HLine)
        self.line1.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line1.setObjectName("line1")
        self.imuLayout.addWidget(self.line1)

        # CSV
        self.labelcsvIMUTitle = QtWidgets.QLabel(self.frameIMU)
        self.labelcsvIMUTitle.setObjectName("labelcsvIMUTitle")
        self.labelcsvIMUTitle.setText("IMU.CSV file")
        self.imuLayout.addWidget(self.labelcsvIMUTitle)

        # CSV button
        self.btnSaveCSV = QtWidgets.QPushButton(self.frameIMU)
        self.btnSaveCSV.setObjectName("btnSaveCSV")
        self.btnSaveCSV.setText("🗀 Save .CSV")
        self.imuLayout.addWidget(self.btnSaveCSV)

        self.statusCSV = QtWidgets.QLineEdit(self.frameIMU)
        self.statusCSV.setObjectName("statusCSV")
        self.statusCSV.setReadOnly(True)
        self.statusCSV.setPlaceholderText("No CSV file selected")
        self.imuLayout.addWidget(self.statusCSV)

        # Divider
        self.line2 = QtWidgets.QFrame(self.frameIMU)
        self.line2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line2.setObjectName("line2")
        self.imuLayout.addWidget(self.line2)

        self.imuLayout.addStretch()

        # =========================================================
        # LIVE IMU VALUES
        # =========================================================

        # Acceleration
        self.labelAccTitle = QtWidgets.QLabel("Acceleration", self.frameIMU)
        self.labelAccTitle.setObjectName("labelAccTitle")
        self.imuLayout.addWidget(self.labelAccTitle)

        self.accLayout = QtWidgets.QHBoxLayout()

        self.labelAx = QtWidgets.QLabel("Ax: 0.00", self.frameIMU)
        self.labelAy = QtWidgets.QLabel("Ay: 0.00", self.frameIMU)
        self.labelAz = QtWidgets.QLabel("Az: 0.00", self.frameIMU)

        self.labelAx.setObjectName("labelAx")
        self.labelAy.setObjectName("labelAy")
        self.labelAz.setObjectName("labelAz")

        self.accLayout.addWidget(self.labelAx)
        self.accLayout.addWidget(self.labelAy)
        self.accLayout.addWidget(self.labelAz)

        self.imuLayout.addLayout(self.accLayout)

        # Gyroscope
        self.labelGyroTitle = QtWidgets.QLabel("Gyroscope", self.frameIMU)
        self.labelGyroTitle.setObjectName("labelGyroTitle")
        self.imuLayout.addWidget(self.labelGyroTitle)

        self.gyroLayout = QtWidgets.QHBoxLayout()

        self.labelGx = QtWidgets.QLabel("Gx: 0.00", self.frameIMU)
        self.labelGy = QtWidgets.QLabel("Gy: 0.00", self.frameIMU)
        self.labelGz = QtWidgets.QLabel("Gz: 0.00", self.frameIMU)

        self.labelGx.setObjectName("labelGx")
        self.labelGy.setObjectName("labelGy")
        self.labelGz.setObjectName("labelGz")

        self.gyroLayout.addWidget(self.labelGx)
        self.gyroLayout.addWidget(self.labelGy)
        self.gyroLayout.addWidget(self.labelGz)

        self.imuLayout.addLayout(self.gyroLayout)

        # Magnetometer
        self.labelMagTitle = QtWidgets.QLabel("Magnetometer", self.frameIMU)
        self.labelMagTitle.setObjectName("labelMagTitle")
        self.imuLayout.addWidget(self.labelMagTitle)

        self.magLayout = QtWidgets.QHBoxLayout()

        self.labelMx = QtWidgets.QLabel("Mx: 0.00", self.frameIMU)
        self.labelMy = QtWidgets.QLabel("My: 0.00", self.frameIMU)
        self.labelMz = QtWidgets.QLabel("Mz: 0.00", self.frameIMU)

        self.labelMx.setObjectName("labelMx")
        self.labelMy.setObjectName("labelMy")
        self.labelMz.setObjectName("labelMz")

        self.magLayout.addWidget(self.labelMx)
        self.magLayout.addWidget(self.labelMy)
        self.magLayout.addWidget(self.labelMz)

        self.imuLayout.addLayout(self.magLayout)

        # Quaternion
        self.labelQuatTitle = QtWidgets.QLabel("Quaternion", self.frameIMU)
        self.labelQuatTitle.setObjectName("labelQuatTitle")
        self.imuLayout.addWidget(self.labelQuatTitle)

        self.quatLayout = QtWidgets.QGridLayout()

        self.labelQi = QtWidgets.QLabel("Qi: 0.00", self.frameIMU)
        self.labelQj = QtWidgets.QLabel("Qj: 0.00", self.frameIMU)
        self.labelQk = QtWidgets.QLabel("Qk: 0.00", self.frameIMU)
        self.labelQr = QtWidgets.QLabel("Qr: 1.00", self.frameIMU)

        self.labelQi.setObjectName("labelQi")
        self.labelQj.setObjectName("labelQj")
        self.labelQk.setObjectName("labelQk")
        self.labelQr.setObjectName("labelQr")

        self.quatLayout.addWidget(self.labelQi, 0, 0)
        self.quatLayout.addWidget(self.labelQj, 0, 1)
        self.quatLayout.addWidget(self.labelQk, 1, 0)
        self.quatLayout.addWidget(self.labelQr, 1, 1)

        self.imuLayout.addLayout(self.quatLayout)
        self.imuLayout.addStretch()

        # =========================================================
        # Visualization Frame
        # =========================================================

        self.plotFrame = QtWidgets.QFrame(self.centralWidget)
        self.plotFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.plotFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.plotFrame.setObjectName("plotFrame")
        self.plotFrame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.plotLayout = QtWidgets.QVBoxLayout(self.plotFrame)
        self.plotLayout.setContentsMargins(0, 0, 0, 0)
        self.plotLayout.setSpacing(10)

        # =========================================================
        # Status Line
        # =========================================================
        self.footerFrame = QtWidgets.QFrame(self.centralWidget)
        self.footerFrame.setObjectName("footerFrame")
        self.footerFrame.setFixedHeight(30)

        self.footerLayout = QtWidgets.QHBoxLayout(self.footerFrame)
        self.footerLayout.setContentsMargins(10, 0, 10, 0)
        self.statusLabel = QtWidgets.QLabel(self.footerFrame)
        self.statusLabel.setObjectName("statusLabel")
        self.statusLabel.setText("● STATUS: DISCONNECTED")
        self.footerLayout.addWidget(self.statusLabel)
        self.footerLayout.addStretch()
        self.centralLayout.addWidget(self.footerFrame)

        # =========================================================
        # Main Layout
        # =========================================================
        self.frameIMU.setFixedWidth(250)

        self.mainLayout.addWidget(self.frameIMU, 0)
        self.mainLayout.addWidget(self.plotFrame, 1)

        self.plot3D()

        # init Events and variables
        self.event_refreshports_clicked()
        self.serial = None
        self.currentMode = None
        self.COMport = None
        self.COMbaudrate = None
        self.csvFilePath = None
        self.csvSavingEnabled = False
        self.csvHeader = False

        self.rxBuffer = ""

        # Button events
        self.btnRefreshPorts.clicked.connect(self.event_refreshports_clicked)
        self.btnConnect.clicked.connect(self.event_connectport_clicked)
        self.btnSaveCSV.clicked.connect(self.event_savecsv_clicked)

        self.serialTimer = QtCore.QTimer(IMUWindow)
        self.serialTimer.setInterval(50)
        self.serialTimer.timeout.connect(self.readSerialData)

    def event_refreshports_clicked(self):

        self.comboSerialPort.clear()
        ports = list_ports.comports()
        for port in ports:
            self.comboSerialPort.addItem(port.device)
        if self.comboSerialPort.count() == 0:
            self.comboSerialPort.addItem("No COM ports")

    def event_connectport_clicked(self):

        if self.serial is not None and self.serial.is_open:
            self.serial.close()
            self.serial = None
            self.btnConnect.setText("Connect")
            self.statusLabel.setText(f" ●  STATUS: DISCONNECTED.")
            self.angleText.SetText(3, f"Angle: 0.00°")

            self.labelAx.setText(f"Ax: 0.00")
            self.labelAy.setText(f"Ay: 0.00")
            self.labelAz.setText(f"Az: 0.00")
            self.labelGx.setText(f"Gx: 0.00")
            self.labelGy.setText(f"Gy: 0.00")
            self.labelGz.setText(f"Gz: 0.00")
            self.labelMx.setText(f"Mx: 0.00")
            self.labelMy.setText(f"My: 0.00")
            self.labelMz.setText(f"Mz: 0.00")
            self.labelQi.setText(f"Qi: 0.00")
            self.labelQj.setText(f"Qj: 0.00")
            self.labelQk.setText(f"Qk: 0.00")
            self.labelQr.setText(f"Qr: 0.00")

            return

        try:
            self.COMport = self.comboSerialPort.currentData()
            if self.COMport is None:
                self.COMport = self.comboSerialPort.currentText().split(" ")[0]
            self.COMbaudrate = int(self.lineBaudrate.text())

            self.serial = Serial(
                port=self.COMport,
                baudrate=self.COMbaudrate,
                timeout=0.1
            )

            self.btnConnect.setText("Disconnect")
            self.statusLabel.setText(f" ● STATUS: CONNECTED to {self.COMport} @ {self.COMbaudrate} baud.")

            self.serialTimer.start()

        except SerialException as e:
            self.serial = None
            self.statusLabel.setText(f"Connection failed:\n{e}")

    def readSerialData(self):

        if self.serial is None:
            return

        if not self.serial.is_open:
            return

        try:
            data = self.serial.read(self.serial.in_waiting).decode("utf-8", errors="ignore")

            if not data:
                return

            self.rxBuffer += data

            while "\n" in self.rxBuffer:
                line, self.rxBuffer = self.rxBuffer.split("\n", 1)
                line = line.rstrip("\r").strip()

                if not line:
                    continue

                self.updateIMU_reading(line)

                if self.csvSavingEnabled and self.csvFilePath:
                    self.startSavingterminal(line)

        except SerialException as error:
            self.statusLabel.setText(f"Serial reading error: {error}")
            self.serialTimer.stop()

    def event_savecsv_clicked(self):

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.IMUWindow,
            "Save CSV File",
            "",
            "CSV Files (*.csv)"
        )

        if not file_path:
            self.statusCSV.setText("No CSV file selected")
            self.csvFilePath = None
            self.csvSavingEnabled = False
            return

        if not file_path.lower().endswith(".csv"):
            file_path += ".csv"

        try:
            open(file_path, "w", encoding="utf-8").close()
            self.csvFilePath = file_path
            self.csvSavingEnabled = True
            self.statusCSV.setText(file_path)

        except Exception as error:
            self.csvFilePath = None
            self.csvSavingEnabled = False

            QtWidgets.QMessageBox.warning(
                self.IMUWindow,
                "CSV File Error",
                f"Could not create the CSV file.\n\n{error}"
            )

    def startSavingterminal(self, line):

        self.machinetime = int(time.time())

        parts = line.split(",")

        if len(parts) < 13:
            return

        ax = parts[0].strip()
        ay = parts[1].strip()
        az = parts[1].strip()
        gx = parts[0].strip()
        gy = parts[1].strip()
        gz = parts[1].strip()
        mx = parts[0].strip()
        my = parts[1].strip()
        mz = parts[1].strip()
        qi = parts[0].strip()
        qj = parts[1].strip()
        qk = parts[1].strip()
        qr = parts[0].strip()

        csv_line = f"{self.machinetime},{ay},{az},{gx},{gy},{gz},{mx},{my},{mz},{qi},{qj},{qk},{qr}\n"

        try:
            if not self.csvHeader:
                with open(self.csvFilePath, "w", encoding="utf-8") as file:
                    file.write("Timestamp, Ax, Ay, Az,Gx, Gy, Gz, Mx, My, Mz, Qi, Qj, Qk, Qr\n")
                    file.write(csv_line)

                self.csvHeader = True
            else:
                with open(self.csvFilePath, "a", encoding="utf-8") as file:
                    file.write(csv_line)
            return

        except Exception as error:

            self.csvFilePath = None
            self.csvSavingEnabled = False
            self.csvHeader = False

            QtWidgets.QMessageBox.warning(
                self.IMUWindow,
                "CSV File Error",
                f"Could not save data to the CSV file.\n\n{error}"
            )
            return

    def updateIMU_reading(self, line):

        parts = line.split(",")

        if len(parts) < 13:
            return

        try:
            ax = float(parts[0].strip())
            ay = float(parts[1].strip())
            az = float(parts[2].strip())
            gx = float(parts[3].strip())
            gy = float(parts[4].strip())
            gz = float(parts[5].strip())
            mx = float(parts[6].strip())
            my = float(parts[7].strip())
            mz = float(parts[8].strip())
            qi = float(parts[9].strip())
            qj = float(parts[10].strip())
            qk = float(parts[11].strip())
            qr = float(parts[12].strip())

        except ValueError:
            return

        self.labelAx.setText(f"Ax: {ax:.2f}")
        self.labelAy.setText(f"Ay: {ay:.2f}")
        self.labelAz.setText(f"Az: {az:.2f}")
        self.labelGx.setText(f"Gx: {gx:.2f}")
        self.labelGy.setText(f"Gy: {gy:.2f}")
        self.labelGz.setText(f"Gz: {gz:.2f}")
        self.labelMx.setText(f"Mx: {mx:.2f}")
        self.labelMy.setText(f"My: {my:.2f}")
        self.labelMz.setText(f"Mz: {mz:.2f}")
        self.labelQi.setText(f"Qi: {qi:.2f}")
        self.labelQj.setText(f"Qj: {qj:.2f}")
        self.labelQk.setText(f"Qk: {qk:.2f}")
        self.labelQr.setText(f"Qr: {qr:.2f}")

        self.upload3dplot(qi, qj, qk, qr)

    def plot3D(self):

        self.plotter3D = pvqt.QtInteractor(self.plotFrame)
        self.plotter3D.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.plotLayout.addWidget(self.plotter3D)

        self.pipeMeshOriginal = pv.Cylinder(center=(0, 0, 0), direction=(1, 0, 0), radius=0.3, height=2.5,
                                            resolution=100)
        self.pipeMesh = self.pipeMeshOriginal.copy()
        self.pipeActor = self.plotter3D.add_mesh(self.pipeMesh, color="lightblue", opacity=0.5, show_edges=True)

        self.angleText = self.plotter3D.add_text("Angle: 0.00°", position="upper_right", font_size=15)

        self.plotter3D.add_axes()
        self.plotter3D.view_yx()
        self.plotter3D.camera.Roll(180)
        self.plotter3D.enable_trackball_style()
        self.plotter3D.camera.zoom(0.8)

    def quaternionToEuler(self, qi, qj, qk, qr):

        norm = np.sqrt(qi ** 2 + qj ** 2 + qk ** 2 + qr ** 2)

        if norm == 0:
            return 0.0, 0.0, 0.0

        qi /= norm
        qj /= norm
        qk /= norm
        qr /= norm

        # X - Roll
        roll = np.arctan2(
            2 * (qr * qi + qj * qk),
            1 - 2 * (qi ** 2 + qj ** 2)
        )

        # Y - Pitch
        sinp = 2 * (qr * qj - qk * qi)
        sinp = np.clip(sinp, -1.0, 1.0)
        pitch = np.arcsin(sinp)

        # Z - Yaw
        yaw = np.arctan2(
            2 * (qr * qk + qi * qj),
            1 - 2 * (qj ** 2 + qk ** 2)
        )

        return np.degrees(roll), np.degrees(pitch), np.degrees(yaw)

    def upload3dplot(self, qi, qj, qk, qr):

        roll, pitch, yaw = self.quaternionToEuler(qi, qj, qk, qr)

        angle_deg = pitch
        visual_angle = 90 - angle_deg

        self.pipeActor.SetOrientation(0, 0, visual_angle)

        self.angleText.SetText(3, f"Angle: {-angle_deg:.2f}°")
        self.plotter3D.render()