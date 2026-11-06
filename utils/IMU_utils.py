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


class IMUSerialReader(QtCore.QThread):
    connected = QtCore.pyqtSignal()
    packets = QtCore.pyqtSignal(object)
    connection_error = QtCore.pyqtSignal(str)
    warning = QtCore.pyqtSignal(str)

    def __init__(self, port, baudrate, parent=None):
        super().__init__(parent)
        self.port = port
        self.baudrate = baudrate
        self._stop_requested = False

    def stop(self):
        self._stop_requested = True

    def run(self):
        # Open and close the COM port in this worker thread only.
        pending = []
        rx = bytearray()
        try:
            with Serial(port=self.port, baudrate=self.baudrate, timeout=0.1) as ser:
                self.connected.emit()
                last_emit = time.monotonic()

                while not self._stop_requested:
                    count = min(max(ser.in_waiting, 1), 4096)
                    data = ser.read(count)
                    if data:
                        rx.extend(data)
                        while True:
                            # Accept '\n', '\r\n', or '\r' as packet separators.
                            n_pos = rx.find(b"\n")
                            r_pos = rx.find(b"\r")
                            ends = [pos for pos in (n_pos, r_pos) if pos >= 0]
                            if not ends:
                                break
                            end = min(ends)
                            packet = bytes(rx[:end]).decode("utf-8", errors="replace").strip()
                            del rx[:end + 1]
                            if packet:
                                pending.append(packet)

                        # Prevent runaway memory usage if the device never sends '\n'.
                        if len(rx) > 8192:
                            preview = bytes(rx[:120]).decode("utf-8", errors="replace")
                            self.warning.emit(
                                f"No newline found in >8192 serial bytes. "
                                f"Check the IMU firmware protocol. Prefix: {preview!r}"
                            )
                            rx.clear()

                    now = time.monotonic()
                    if pending and (now - last_emit >= 0.05 or len(pending) >= 64):
                        self.packets.emit(pending)
                        pending = []
                        last_emit = now

                if pending:
                    self.packets.emit(pending)
        except (SerialException, OSError, ValueError) as exc:
            self.connection_error.emit(str(exc))


def parse_imu_packet(line):
    """Expected firmware format: Ax,Ay,Az,Gx,Gy,Gz,Mx,My,Mz,Qi,Qj,Qk,Qr."""
    fields = line.split(",")
    if len(fields) < 13:
        return None
    try:
        values = tuple(float(value.strip()) for value in fields[:13])
    except ValueError:
        return None
    if not all(np.isfinite(value) for value in values):
        return None
    return values


class UI_IMUWindow(object):

    def setupIMU_UI(self, IMUWindow):

        self.IMUWindow = IMUWindow

        IMUWindow.setObjectName("IMUWindow")
        IMUWindow.resize(700, 500)
        IMUWindow.setStyleSheet(STYLEsheet)
        IMUWindow.setWindowTitle("IMU Serial Monitor")

        self.thread = None
        self.worker = None
        self._latest_line = None
        self.validPacketCount = 0
        self.invalidPacketCount = 0
        self._last_status_print = time.monotonic()
        self._last_data_time = None
        self._last_error = None
        self._warning_count = 0
        self._last_valid_sample = None
        self._previous_report_quaternion = None

        # PyVista rendering configuration
        self.render_fps = 20
        self.render_interval = 1.0 / self.render_fps
        self._last_render = 0.0

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

        self.displayTimer = QtCore.QTimer(IMUWindow)
        self.displayTimer.setInterval(50)  # max 20 GUI updates per second
        self.displayTimer.timeout.connect(self.refreshIMU_display)

        # shutdown event
        app = QtWidgets.QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.shutdown)

    def event_refreshports_clicked(self):

        previous_port = self.comboSerialPort.currentText()
        self.comboSerialPort.clear()
        ports = list_ports.comports()
        for port in ports:
            self.comboSerialPort.addItem(port.device)
        if self.comboSerialPort.count() == 0:
            self.comboSerialPort.addItem("No COM ports")
        else:
            # Keep the previous selection; otherwise prefer the IMU's known COM5.
            preferred = previous_port if self.comboSerialPort.findText(previous_port) >= 0 else "COM5"
            index = self.comboSerialPort.findText(preferred)
            if index >= 0:
                self.comboSerialPort.setCurrentIndex(index)

    def event_connectport_clicked(self):
        # The serial port belongs exclusively to IMUSerialReader, never this GUI.
        if self.thread is not None:
            if self.thread.isRunning():
                self.btnConnect.setEnabled(False)
                self.statusLabel.setText("● STATUS: DISCONNECTING...")
                self.thread.stop()
            return

        port = self.comboSerialPort.currentText().strip()
        if not port or port == "No COM ports":
            self.statusLabel.setText("● STATUS: Select a valid IMU COM port")
            return
        try:
            baudrate = int(self.lineBaudrate.text().strip())
            if baudrate <= 0:
                raise ValueError("Baud rate must be positive")
        except ValueError as exc:
            self.statusLabel.setText(f"● STATUS: Invalid baud rate: {exc}")
            return

        self.COMport = port
        self.COMbaudrate = baudrate
        self.validPacketCount = 0
        self.invalidPacketCount = 0
        self._warning_count = 0
        self._last_data_time = None
        self._last_error = None
        self._latest_line = None
        self._last_valid_sample = None
        self._previous_report_quaternion = None
        self._last_status_print = time.monotonic()

        self.thread = IMUSerialReader(port, baudrate, self.IMUWindow)
        # Force delivery to Qt's GUI thread, never the serial worker thread.
        queued = QtCore.Qt.QueuedConnection
        self.thread.connected.connect(self._serial_connected, queued)
        self.thread.packets.connect(self._serial_packets, queued)
        self.thread.warning.connect(self._serial_warning, queued)
        self.thread.connection_error.connect(self._serial_error, queued)
        self.thread.finished.connect(self._serial_finished, queued)

        self.btnConnect.setEnabled(False)
        self.statusLabel.setText(f"● STATUS: CONNECTING to {port}...")
        print(f"[IMU] Opening {port} at {baudrate} baud...", flush=True)
        self.thread.start()

    def _serial_connected(self):
        if self.thread is None or self.thread._stop_requested:
            return
        self.btnConnect.setEnabled(True)
        self.btnConnect.setText("Disconnect")
        self.statusLabel.setText(
            f"● STATUS: CONNECTED to {self.COMport} @ {self.COMbaudrate}; waiting for packets"
        )
        self.displayTimer.start()
        print(f"[IMU] Connected to {self.COMport}; expecting 13 comma-separated values per line.", flush=True)

    def _serial_packets(self, lines):
        # Called in GUI thread as a queued Qt signal; no serial access here.
        latest_valid = None
        for line in lines:
            parsed = parse_imu_packet(line)
            if parsed is None:
                self.invalidPacketCount += 1
                if self.invalidPacketCount <= 5:
                    print(f"[IMU] INVALID packet #{self.invalidPacketCount}: {line[:180]!r}", flush=True)
                continue

            self.validPacketCount += 1
            latest_valid = line
            self._last_valid_sample = parsed
            self._last_data_time = time.monotonic()
            if self.validPacketCount == 1:
                print(f"[IMU] First valid sample received on {self.COMport}: {line[:180]}", flush=True)
            if self.csvSavingEnabled and self.csvFilePath:
                self.startSavingterminal(line)

        if latest_valid is not None:
            self._latest_line = latest_valid  # coalesce UI updates, preserve every CSV packet

        now = time.monotonic()
        if now - self._last_status_print >= 2.0:
            if self._last_valid_sample is not None:
                q = self._last_valid_sample[9:13]
                _, pitch, _ = self.quaternionToEuler(*q)
                changed = (
                        self._previous_report_quaternion is None
                        or any(abs(x - y) > 1e-6 for x, y in zip(q, self._previous_report_quaternion))
                )
                info = (f"pitch={pitch:.2f} deg; q={tuple(round(v, 4) for v in q)}; "
                        f"quaternion_changed={changed}")
                self._previous_report_quaternion = q
            else:
                info = "no valid IMU packets received"
            print(
                f"[IMU] valid={self.validPacketCount}, invalid={self.invalidPacketCount}; {info}",
                flush=True,
            )
            self._last_status_print = now

    def refreshIMU_display(self):
        # Render only the most recent complete packet: <=20 FPS.
        if self._latest_line is not None:
            line = self._latest_line
            self._latest_line = None
            self.updateIMU_reading(line)
            self.statusLabel.setText(
                f"● STATUS: {self.COMport} connected | "
                f"valid={self.validPacketCount} invalid={self.invalidPacketCount}"
            )
            print(line)
        elif self.validPacketCount == 0 and time.monotonic() - self._last_status_print > 2.0:
            print(
                f"[IMU] Still waiting for valid 13-field CSV packets on {self.COMport}. "
                f"Check firmware output, baud rate and line terminators.",
                flush=True,
            )
            self._last_status_print = time.monotonic()

    def _serial_warning(self, message):
        self._warning_count += 1
        if self._warning_count <= 5:
            print(f"[IMU] WARNING: {message}", flush=True)
        self.statusLabel.setText("● STATUS: Serial framing error; see terminal")

    def _serial_error(self, message):
        self._last_error = message
        self.statusLabel.setText(f"● STATUS: Serial error: {message}")
        print(f"[IMU] ERROR: {message}", flush=True)

    def _serial_finished(self):
        self.displayTimer.stop()
        self.btnConnect.setText("Connect")
        self.btnConnect.setEnabled(True)
        if self._last_error is None:
            self.statusLabel.setText("● STATUS: DISCONNECTED")
        self.thread = None
        self._latest_line = None
        print("[IMU] Serial reader stopped; port released.", flush=True)

    def shutdown(self):
        """Release COM5 on normal application exit (no GUI access from worker)."""
        if hasattr(self, "displayTimer"):
            self.displayTimer.stop()
        if self.thread is not None and self.thread.isRunning():
            self.thread.stop()
            if not self.thread.wait(2000):
                print("[IMU] WARNING: serial reader did not exit within 2 seconds.", flush=True)
                # Do not forcibly terminate a QThread while it owns a serial port.

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
        """Save each valid IMU sample in exact firmware-field order."""
        sample = parse_imu_packet(line)
        if sample is None or not self.csvFilePath:
            return

        row = f"{time.time():.3f}," + ",".join(f"{value:.9g}" for value in sample) + "\n"
        header = "Timestamp,Ax,Ay,Az,Gx,Gy,Gz,Mx,My,Mz,Qi,Qj,Qk,Qr\n"
        try:
            if not self.csvHeader:
                with open(self.csvFilePath, "w", encoding="utf-8") as file:
                    file.write(header)
                    file.write(row)
                self.csvHeader = True
            else:
                with open(self.csvFilePath, "a", encoding="utf-8") as file:
                    file.write(row)
        except OSError as exc:
            self.csvFilePath = None
            self.csvSavingEnabled = False
            self.csvHeader = False
            QtWidgets.QMessageBox.warning(
                self.IMUWindow, "CSV File Error", f"Could not save data to the CSV file.\n\n{exc}"
            )

    def updateIMU_reading(self, line):
        """Update numerical labels and the pitch-only PyVista visualization."""
        sample = parse_imu_packet(line)
        if sample is None:
            return

        ax, ay, az, gx, gy, gz, mx, my, mz, qi, qj, qk, qr = sample

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

        now = time.monotonic()
        if now - self._last_render >= self.render_interval:
            self.upload3dplot(qi, qj, qk, qr)
            self._last_render = now

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