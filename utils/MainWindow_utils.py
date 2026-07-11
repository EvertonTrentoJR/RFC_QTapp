# import relevant packages
from PyQt5 import QtCore, QtGui, QtWidgets
from pathlib import Path
from serial import Serial, SerialException
from serial.tools import list_ports

# Load the stylesheet once when this module is imported
_STYLE_PATH = Path(__file__).parent / "stylesheet.qss"

with open(_STYLE_PATH, "r", encoding="utf-8") as f:
    STYLEsheet = f.read()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1201, 770)
        MainWindow.setStyleSheet(STYLEsheet)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_root = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_root.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_root.setSpacing(0)
        self.verticalLayout_root.setObjectName("verticalLayout_root")
        self.headerFrame = QtWidgets.QFrame(self.centralwidget)
        self.headerFrame.setMinimumSize(QtCore.QSize(0, 78))
        self.headerFrame.setMaximumSize(QtCore.QSize(16777215, 78))
        self.headerFrame.setObjectName("headerFrame")
        self.horizontalLayout_header = QtWidgets.QHBoxLayout(self.headerFrame)
        self.horizontalLayout_header.setContentsMargins(16, -1, 24, -1)
        self.horizontalLayout_header.setObjectName("horizontalLayout_header")
        self.logoLabel = QtWidgets.QLabel(self.headerFrame)
        self.logoLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.logoLabel.setObjectName("logoLabel")
        self.horizontalLayout_header.addWidget(self.logoLabel)
        self.groupLabel = QtWidgets.QLabel(self.headerFrame)
        self.groupLabel.setStyleSheet("font-size:28px;font-weight:bold;")
        self.groupLabel.setObjectName("groupLabel")
        self.horizontalLayout_header.addWidget(self.groupLabel)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_header.addItem(spacerItem)
        self.titleLabel = QtWidgets.QLabel(self.headerFrame)
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setObjectName("titleLabel")
        self.horizontalLayout_header.addWidget(self.titleLabel)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_header.addItem(spacerItem1)
        self.creditLabel = QtWidgets.QLabel(self.headerFrame)
        self.creditLabel.setObjectName("creditLabel")
        self.creditLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.horizontalLayout_header.addWidget(self.creditLabel)
        self.verticalLayout_root.addWidget(self.headerFrame)
        self.bodyFrame = QtWidgets.QFrame(self.centralwidget)
        self.bodyFrame.setObjectName("bodyFrame")
        self.horizontalLayout_body = QtWidgets.QHBoxLayout(self.bodyFrame)
        self.horizontalLayout_body.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_body.setSpacing(0)
        self.horizontalLayout_body.setObjectName("horizontalLayout_body")

        self.sidebarFrame = QtWidgets.QFrame(self.bodyFrame)
        self.sidebarFrame.setMinimumSize(QtCore.QSize(230, 0))
        self.sidebarFrame.setMaximumSize(QtCore.QSize(230, 16777215))
        self.sidebarFrame.setObjectName("sidebarFrame")
        self.verticalLayout_sidebar = QtWidgets.QVBoxLayout(self.sidebarFrame)
        self.verticalLayout_sidebar.setContentsMargins(18, 24, 18, 24)
        self.verticalLayout_sidebar.setSpacing(10)
        self.verticalLayout_sidebar.setObjectName("verticalLayout_sidebar")
        self.menuTitle = QtWidgets.QLabel(self.sidebarFrame)
        self.menuTitle.setObjectName("menuTitle")
        self.verticalLayout_sidebar.addWidget(self.menuTitle)
        self.btnRFC = QtWidgets.QPushButton(self.sidebarFrame)
        self.btnRFC.setCheckable(True)
        self.btnRFC.setObjectName("btnRFC")
        self.verticalLayout_sidebar.addWidget(self.btnRFC)
        self.btnAngle = QtWidgets.QPushButton(self.sidebarFrame)
        self.btnAngle.setCheckable(True)
        self.btnAngle.setObjectName("btnAngle")
        self.verticalLayout_sidebar.addWidget(self.btnAngle)
        self.btnHome = QtWidgets.QPushButton(self.sidebarFrame)
        self.btnHome.setCheckable(True)
        self.btnHome.setObjectName("btnHome")
        self.verticalLayout_sidebar.addWidget(self.btnHome)
        self.line1 = QtWidgets.QFrame(self.sidebarFrame)
        self.line1.setFrameShape(QtWidgets.QFrame.HLine)
        self.line1.setObjectName("line1")
        self.verticalLayout_sidebar.addWidget(self.line1)
        self.connectionTitle = QtWidgets.QLabel(self.sidebarFrame)
        self.connectionTitle.setObjectName("connectionTitle")
        self.verticalLayout_sidebar.addWidget(self.connectionTitle)
        self.serialPortLabel = QtWidgets.QLabel(self.sidebarFrame)
        self.serialPortLabel.setObjectName("serialPortLabel")
        self.verticalLayout_sidebar.addWidget(self.serialPortLabel)
        self.horizontalLayout_serialPort = QtWidgets.QHBoxLayout()
        self.horizontalLayout_serialPort.setObjectName("horizontalLayout_serialPort")
        self.comboSerialPort = QtWidgets.QComboBox(self.sidebarFrame)
        self.comboSerialPort.setObjectName("comboSerialPort")
        self.comboSerialPort.addItem("")
        self.comboSerialPort.addItem("")
        self.comboSerialPort.addItem("")
        self.horizontalLayout_serialPort.addWidget(self.comboSerialPort)
        self.btnRefreshPorts = QtWidgets.QPushButton(self.sidebarFrame)
        self.btnRefreshPorts.setObjectName("btnRefreshPorts")
        self.horizontalLayout_serialPort.addWidget(self.btnRefreshPorts)
        self.verticalLayout_sidebar.addLayout(self.horizontalLayout_serialPort)
        self.baudLabel = QtWidgets.QLabel(self.sidebarFrame)
        self.baudLabel.setObjectName("baudLabel")
        self.verticalLayout_sidebar.addWidget(self.baudLabel)
        self.lineBaudrate = QtWidgets.QLineEdit(self.sidebarFrame)
        self.lineBaudrate.setObjectName("lineBaudrate")
        self.verticalLayout_sidebar.addWidget(self.lineBaudrate)
        self.btnConnect = QtWidgets.QPushButton(self.sidebarFrame)
        self.btnConnect.setObjectName("btnConnect")
        self.verticalLayout_sidebar.addWidget(self.btnConnect)
        self.line2 = QtWidgets.QFrame(self.sidebarFrame)
        self.line2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line2.setObjectName("line2")
        self.verticalLayout_sidebar.addWidget(self.line2)
        self.controlTitle = QtWidgets.QLabel(self.sidebarFrame)
        self.controlTitle.setObjectName("controlTitle")
        self.verticalLayout_sidebar.addWidget(self.controlTitle)
        self.btnStart = QtWidgets.QPushButton(self.sidebarFrame)
        self.btnStart.setObjectName("btnStart")
        self.verticalLayout_sidebar.addWidget(self.btnStart)
        self.btnStop = QtWidgets.QPushButton(self.sidebarFrame)
        self.btnStop.setEnabled(False)
        self.btnStop.setObjectName("btnStop")
        self.verticalLayout_sidebar.addWidget(self.btnStop)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_sidebar.addItem(spacerItem2)
        self.horizontalLayout_body.addWidget(self.sidebarFrame)
        self.mainFrame = QtWidgets.QFrame(self.bodyFrame)
        self.mainFrame.setObjectName("mainFrame")
        self.verticalLayout_main = QtWidgets.QVBoxLayout(self.mainFrame)
        self.verticalLayout_main.setContentsMargins(22, 24, 22, 24)
        self.verticalLayout_main.setSpacing(20)
        self.verticalLayout_main.setObjectName("verticalLayout_main")

        self.cardsLayout = QtWidgets.QHBoxLayout()
        self.cardsLayout.setSpacing(14)
        self.cardsLayout.setObjectName("cardsLayout")

        self.cardAng = QtWidgets.QFrame(self.mainFrame)
        self.cardAng.setObjectName("cardAng")
        self.cardLayout1 = QtWidgets.QVBoxLayout(self.cardAng)
        self.cardLayout1.setObjectName("cardLayout1")
        self.Ang_label = QtWidgets.QLabel(self.cardAng)
        self.Ang_label.setAlignment(QtCore.Qt.AlignCenter)
        self.Ang_label.setObjectName("Ang_label")
        self.cardLayout1.addWidget(self.Ang_label, 0, QtCore.Qt.AlignTop)
        self.Ang_value = QtWidgets.QDoubleSpinBox(self.cardAng)
        self.Ang_value.setObjectName("Ang_value")
        self.Ang_value.setDecimals(0)
        self.Ang_value.setSingleStep(1)
        self.Ang_value.setValue(45)
        self.cardLayout1.addWidget(self.Ang_value, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.Ang_unit = QtWidgets.QLabel(self.cardAng)
        self.Ang_unit.setAlignment(QtCore.Qt.AlignCenter)
        self.Ang_unit.setObjectName("Ang_unit")
        self.cardLayout1.addWidget(self.Ang_unit)
        self.cardsLayout.addWidget(self.cardAng)

        self.cardVeloc = QtWidgets.QFrame(self.mainFrame)
        self.cardVeloc.setStyleSheet("QLabel#cardTitle1{font-size:13px;font-weight:bold;} QLabel#cardNumber1{font-size:26px;font-weight:bold;}")
        self.cardVeloc.setObjectName("cardVeloc")
        self.cardLayout2 = QtWidgets.QVBoxLayout(self.cardVeloc)
        self.cardLayout2.setObjectName("cardLayout2")
        self.Veloc_label = QtWidgets.QLabel(self.cardVeloc)
        self.Veloc_label.setAlignment(QtCore.Qt.AlignCenter)
        self.Veloc_label.setObjectName("Veloc_label")
        self.cardLayout2.addWidget(self.Veloc_label, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.Veloc_value = QtWidgets.QDoubleSpinBox(self.cardVeloc)
        self.Veloc_value.setObjectName("Veloc_value")
        self.Veloc_value.setDecimals(0)
        self.Veloc_value.setSingleStep(1)
        self.Veloc_value.setValue(45)
        self.cardLayout2.addWidget(self.Veloc_value, 0, QtCore.Qt.AlignHCenter)
        self.Veloc_unit = QtWidgets.QLabel(self.cardVeloc)
        self.Veloc_unit.setAlignment(QtCore.Qt.AlignCenter)
        self.Veloc_unit.setObjectName("Veloc_unit")
        self.cardLayout2.addWidget(self.Veloc_unit)
        self.cardsLayout.addWidget(self.cardVeloc)

        self.cardAcc = QtWidgets.QFrame(self.mainFrame)
        self.cardAcc.setObjectName("cardAcc")
        self.cardLayout3 = QtWidgets.QVBoxLayout(self.cardAcc)
        self.cardLayout3.setObjectName("cardLayout3")
        self.Acc_label = QtWidgets.QLabel(self.cardAcc)
        self.Acc_label.setAlignment(QtCore.Qt.AlignCenter)
        self.Acc_label.setObjectName("Acc_label")
        self.cardLayout3.addWidget(self.Acc_label, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.Acc_value = QtWidgets.QDoubleSpinBox(self.cardAcc)
        self.Acc_value.setObjectName("Acc_value")
        self.Acc_value.setSingleStep(0.01)
        self.Acc_value.setValue(0.33)
        self.cardLayout3.addWidget(self.Acc_value, 0, QtCore.Qt.AlignHCenter)
        self.Acc_unit = QtWidgets.QLabel(self.cardAcc)
        self.Acc_unit.setAlignment(QtCore.Qt.AlignCenter)
        self.Acc_unit.setObjectName("Acc_unit")
        self.cardLayout3.addWidget(self.Acc_unit)
        self.cardsLayout.addWidget(self.cardAcc)

        self.cardReps = QtWidgets.QFrame(self.mainFrame)
        self.cardReps.setObjectName("cardReps")
        self.cardLayout4 = QtWidgets.QVBoxLayout(self.cardReps)
        self.cardLayout4.setObjectName("cardLayout4")
        self.Reps_label = QtWidgets.QLabel(self.cardReps)
        self.Reps_label.setAlignment(QtCore.Qt.AlignCenter)
        self.Reps_label.setObjectName("Reps_label")
        self.cardLayout4.addWidget(self.Reps_label, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.Reps_value = QtWidgets.QDoubleSpinBox(self.cardReps)
        self.Reps_value.setObjectName("Reps_value")
        self.Reps_value.setDecimals(0)
        self.Reps_value.setSingleStep(1)
        self.Reps_value.setValue(45)
        self.cardLayout4.addWidget(self.Reps_value, 0, QtCore.Qt.AlignHCenter)
        self.Reps_unit = QtWidgets.QLabel(self.cardReps)
        self.Reps_unit.setAlignment(QtCore.Qt.AlignCenter)
        self.Reps_unit.setText("Reps")
        self.Reps_unit.setObjectName("Reps_unit")
        self.cardLayout4.addWidget(self.Reps_unit)
        self.cardsLayout.addWidget(self.cardReps)

        self.cardDTime = QtWidgets.QFrame(self.mainFrame)
        self.cardDTime.setObjectName("cardDTime")
        self.cardLayout5 = QtWidgets.QVBoxLayout(self.cardDTime)
        self.cardLayout5.setObjectName("cardLayout5")
        self.DTime_label = QtWidgets.QLabel(self.cardDTime)
        self.DTime_label.setAlignment(QtCore.Qt.AlignCenter)
        self.DTime_label.setObjectName("DTime_label")
        self.cardLayout5.addWidget(self.DTime_label, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.DTime_value = QtWidgets.QDoubleSpinBox(self.cardDTime)
        self.DTime_value.setObjectName("DTime_value")
        self.DTime_value.setDecimals(0)
        self.DTime_value.setSingleStep(1)
        self.DTime_value.setValue(60)
        self.cardLayout5.addWidget(self.DTime_value, 0, QtCore.Qt.AlignHCenter)
        self.DTime_unit = QtWidgets.QLabel(self.cardDTime)
        self.DTime_unit.setAlignment(QtCore.Qt.AlignCenter)
        self.DTime_unit.setObjectName("DTime_unit")
        self.cardLayout5.addWidget(self.DTime_unit)
        self.cardsLayout.addWidget(self.cardDTime)



        self.verticalLayout_main.addLayout(self.cardsLayout)
        self.consoleFrame = QtWidgets.QFrame(self.mainFrame)
        self.consoleFrame.setMinimumSize(QtCore.QSize(0, 150))
        self.consoleFrame.setObjectName("consoleFrame")
        self.consoleLayout = QtWidgets.QVBoxLayout(self.consoleFrame)
        self.consoleLayout.setContentsMargins(10, 10, 10, 10)
        self.consoleLayout.setSpacing(6)
        self.consoleOutput = QtWidgets.QPlainTextEdit(self.consoleFrame)
        self.consoleOutput.setReadOnly(True)
        self.consoleOutput.setObjectName("consoleOutput")
        self.commandLine = QtWidgets.QLineEdit(self.consoleFrame)
        self.commandLine.setObjectName("commandLine")
        self.commandLine.setPlaceholderText("Type a command and press Start...")
        self.consoleLayout.addWidget(self.consoleOutput)
        self.consoleLayout.addWidget(self.commandLine)
        self.verticalLayout_console = QtWidgets.QVBoxLayout(self.consoleFrame)
        self.verticalLayout_console.setObjectName("verticalLayout_console")
        self.plainConsole = QtWidgets.QPlainTextEdit(self.consoleFrame)
        self.plainConsole.setEnabled(False)
        self.plainConsole.setReadOnly(True)
        self.plainConsole.setObjectName("plainConsole")
        self.verticalLayout_console.addWidget(self.plainConsole)
        self.verticalLayout_main.addWidget(self.consoleFrame)
        self.horizontalLayout_body.addWidget(self.mainFrame)
        self.verticalLayout_root.addWidget(self.bodyFrame)
        self.footerFrame = QtWidgets.QFrame(self.centralwidget)
        self.footerFrame.setMaximumSize(QtCore.QSize(16777215, 32))
        self.footerFrame.setObjectName("footerFrame")
        self.horizontalLayout_footer = QtWidgets.QHBoxLayout(self.footerFrame)
        self.horizontalLayout_footer.setObjectName("horizontalLayout_footer")
        spacerItem3 = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_footer.addItem(spacerItem3)
        self.statusLabel = QtWidgets.QLabel(self.footerFrame)
        self.statusLabel.setObjectName("statusLabel")
        self.horizontalLayout_footer.addWidget(self.statusLabel)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_footer.addItem(spacerItem4)
        self.verticalLayout_root.addWidget(self.footerFrame)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # init Events
        self.event_refreshports_clicked()
        self.serial = None
        self.currentMode = None
        self.COMport = None
        self.COMbaudrate = None

        self.serialTimer = QtCore.QTimer(MainWindow)
        self.serialTimer.setInterval(50)
        self.serialTimer.timeout.connect(self.readSerialData)

    # Events
        self.Ang_value.valueChanged.connect( lambda: self.updateCommandLine(self.currentMode))
        self.Veloc_value.valueChanged.connect( lambda: self.updateCommandLine(self.currentMode))
        self.Acc_value.valueChanged.connect( lambda: self.updateCommandLine(self.currentMode))
        self.DTime_value.valueChanged.connect( lambda: self.updateCommandLine(self.currentMode))
        self.Reps_value.valueChanged.connect( lambda: self.updateCommandLine(self.currentMode))

    # Button events
        self.btnRFC.clicked.connect(self.event_rfc_clicked)
        self.btnAngle.clicked.connect(self.event_angle_clicked)
        self.btnHome.clicked.connect(self.event_home_clicked)

        self.btnRefreshPorts.clicked.connect(self.event_refreshports_clicked)
        self.btnConnect.clicked.connect(self.event_connectport_clicked)
        self.btnStart.clicked.connect(self.event_start_clicked)
        self.btnStop.clicked.connect(self.event_stop_clicked)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "RFC Control Panel"))
        self.logoLabel.setText(_translate("MainWindow", "RFC"))
        self.groupLabel.setText(_translate("MainWindow", "StepperMotor"))
        self.titleLabel.setText(_translate("MainWindow", " CONTROL PANEL"))
        self.creditLabel.setText(_translate("MainWindow","Powered by LASII | Debugged by AI"))
        self.menuTitle.setText(_translate("MainWindow", "TEST SELECTION"))
        self.btnRFC.setText(_translate("MainWindow", "  ∿   RFC"))
        self.btnAngle.setText(_translate("MainWindow", "  ∠   ANGLE"))
        self.btnHome.setText(_translate("MainWindow", "  ⌂   HOME"))
        self.connectionTitle.setText(_translate("MainWindow", "COM CONNECTION"))
        self.serialPortLabel.setText(_translate("MainWindow", "Serial Port"))
        self.comboSerialPort.setItemText(0, _translate("MainWindow", "--"))
        self.btnRefreshPorts.setToolTip(_translate("MainWindow", "Refresh COM ports"))
        self.btnRefreshPorts.setText(_translate("MainWindow", "↻ refresh"))
        self.baudLabel.setText(_translate("MainWindow", "Baud rate"))
        self.lineBaudrate.setText(_translate("MainWindow", "9600"))
        self.btnConnect.setText(_translate("MainWindow", "⛓  CONNECT"))
        self.controlTitle.setText(_translate("MainWindow", "CONTROL"))
        self.btnStart.setText(_translate("MainWindow", "▷  START"))
        self.btnStop.setText(_translate("MainWindow", "■  STOP"))
        self.Veloc_label.setText(_translate("MainWindow", " Velocity"))
        self.Veloc_unit.setText(_translate("MainWindow", "RPM"))
        self.Acc_label.setText(_translate("MainWindow", "Acceleration"))
        self.Acc_unit.setText(_translate("MainWindow", "RPM/s"))
        self.Ang_label.setText(_translate("MainWindow", "Angle"))
        self.Ang_unit.setText(_translate("MainWindow", "Degree"))
        self.DTime_label.setText(_translate("MainWindow", "Delay Time"))
        self.DTime_unit.setText(_translate("MainWindow", "Seconds"))
        self.Reps_label.setText(_translate("MainWindow", "Repetition"))
        self.statusLabel.setText(_translate("MainWindow", "●  STATUS: DISCONNECTED"))

    def event_rfc_clicked(self):
        self.setMode("rfc")

    def event_angle_clicked(self):
        self.setMode("angle")

    def event_home_clicked(self):
        self.setMode("home")

    def setMode(self, mode):

        self.currentMode = mode

        normal = "background-color:#c9c9c9; color:black; border: 1px solid #aaaaaa;"
        selected = "background-color:#707070; color:white; border: 1px solid #5a5a5a; font-weight: bold;"
        self.btnRFC.setStyleSheet(normal)
        self.btnAngle.setStyleSheet(normal)
        self.btnHome.setStyleSheet(normal)

        if mode == "rfc":
            self.cardAcc.setEnabled(True)
            self.cardAng.setEnabled(True)
            self.cardVeloc.setEnabled(True)
            self.cardDTime.setEnabled(False)
            self.cardReps.setEnabled(False)
            self.btnRFC.setStyleSheet(selected)

        elif mode == "angle":
            self.cardAcc.setEnabled(True)
            self.cardAng.setEnabled(True)
            self.cardVeloc.setEnabled(True)
            self.cardDTime.setEnabled(True)
            self.cardReps.setEnabled(True)
            self.btnAngle.setStyleSheet(selected)

        elif mode == "home":
            self.cardAcc.setEnabled(False)
            self.cardAng.setEnabled(False)
            self.cardVeloc.setEnabled(False)
            self.cardDTime.setEnabled(False)
            self.cardReps.setEnabled(False)
            self.btnHome.setStyleSheet(selected)


        self.updateCommandLine(mode)

    def updateCommandLine(self, mode):

        global command

        if self.serial is None:
            self.statusLabel.setText(f"MODE: {self.currentMode} Selected. ●  STATUS: DISCONNECTED")
        else:
            self.statusLabel.setText(
                f"MODE: {self.currentMode} Selected. ●  STATUS: CONNECTED to {self.COMport} @ {self.COMbaudrate} baud.")

        if mode == "home":
            self.commandLine.setText("home")

            return

        elif mode == "rfc":

            command = (
                f"R,"
                f"{int(self.Ang_value.value())},"
                f"{int(self.Veloc_value.value())},"
                f"{self.Acc_value.value()}"
            )

        elif mode == "angle":

            command = (
                f"A,"
                f"{int(self.Ang_value.value())},"
                f"{int(self.Veloc_value.value())},"
                f"{self.Acc_value.value()},"
                f"{int(self.Reps_value.value())},"
                f"{int(self.DTime_value.value())}"
            )

        self.commandLine.setText(command)

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
            self.commandLine.clear()

            if self.currentMode is None:
                self.statusLabel.setText(f" ●  STATUS: DISCONNECTED.")
            else:
                self.statusLabel.setText(
                    f"MODE: {self.currentMode} Selected. ●  STATUS: DISCONNECTED.")
            return
        try:
            self.COMport = self.comboSerialPort.currentData()
            if self.COMport is None:
                self.COMport = self.comboSerialPort.currentText().split(" ")[0]
            self.COMbaudrate = int(self.lineBaudrate.text())

            self.serial = Serial(
                port=self.COMport,
                baudrate=self.COMbaudrate,
                timeout=0
            )

            self.btnConnect.setText("Disconnect")

            if self.currentMode is None:
                self.statusLabel.setText(f" ●  STATUS: CONNECTED to {self.COMport} @ {self.COMbaudrate} baud.")
            else:
                self.statusLabel.setText(f"MODE: {self.currentMode} Selected. ●  STATUS: CONNECTED to {self.COMport} @ {self.COMbaudrate} baud.")

            self.serialTimer.start()

        except SerialException as e:
            self.serial = None
            self.consoleOutput.appendPlainText(
                f"Connection failed:\n{e}"
            )

    def readSerialData(self):

        if self.serial is None:
            return

        if not self.serial.is_open:
            return

        try:
            while self.serial.in_waiting > 0:

                received = self.serial.readline().decode(
                    "utf-8",
                    errors="replace"
                ).strip()

                if received:
                    self.consoleOutput.appendPlainText(
                        f"RX: {received}"
                    )

        except SerialException as error:

            self.consoleOutput.appendPlainText(
                f"Serial reading error: {error}"
            )

            self.serialTimer.stop()

    def sendSerialData(self, data):

        if self.serial is None or not self.serial.is_open:
            QtWidgets.QMessageBox.warning(self.MainWindow,"Serial port is not connected.","Please Connect to a Serial Port before starting.")
            return False

        data = str(data).strip()

        if not data:
            return False

        try:
            self.serial.write((data + "\n").encode("utf-8"))

            self.consoleOutput.appendPlainText(
                f"TX: {data}"
            )

            return True

        except SerialException as error:

            self.consoleOutput.appendPlainText(
                f"Serial sending error: {error}"
            )

            return False

    def event_start_clicked(self):
        if self.serial is None or not self.serial.is_open:
            QtWidgets.QMessageBox.warning(self.MainWindow,"Serial port is not connected.","Please Connect to a Serial Port before starting.")
            return False
        elif self.currentMode is None:
            QtWidgets.QMessageBox.warning(self.MainWindow,"No Mode Selected","Please select an operation mode (RFC, Angle or Home) before starting.")
            return
        else:
            startcommand = self.commandLine.text().strip()
            self.sendSerialData(startcommand)
            self.btnStop.setEnabled(True)
            self.btnStart.setEnabled(False)

    def event_stop_clicked(self):
        self.commandLine.setText("X")
        stopcommand = self.commandLine.text().strip()
        self.sendSerialData(stopcommand)
        self.btnStop.setEnabled(False)
        self.btnStart.setEnabled(True)
        self.commandLine.clear()