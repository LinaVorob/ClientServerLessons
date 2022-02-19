from PyQt5 import QtCore, QtGui, QtWidgets

import server_class
from util import CONFIG


class Ui_Server_int(object):
    def setupUi(self, Server_int):
        Server_int.setObjectName("Server_int")
        Server_int.resize(440, 430)
        Server_int.setMinimumSize(QtCore.QSize(440, 430))
        Server_int.setMaximumSize(QtCore.QSize(440, 430))

        self.tableWidget = QtWidgets.QTableWidget(Server_int)
        self.tableWidget.setGeometry(QtCore.QRect(10, 120, 351, 291))
        self.tableWidget.setRowCount(20)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(['Client', 'Info', 'Status'])
        self.tableWidget.setObjectName("tableWidget")

        self.pushButton = QtWidgets.QPushButton(Server_int)
        self.pushButton.setGeometry(QtCore.QRect(260, 30, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")

        self.label_ip = QtWidgets.QLabel(Server_int)
        self.label_ip.setGeometry(QtCore.QRect(10, 30, 71, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_ip.setFont(font)
        self.label_ip.setAutoFillBackground(True)
        self.label_ip.setObjectName("label_ip")

        self.label_port = QtWidgets.QLabel(Server_int)
        self.label_port.setGeometry(QtCore.QRect(20, 72, 47, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_port.setFont(font)
        self.label_port.setObjectName("label_2")

        self.text_ip = QtWidgets.QTextEdit(Server_int)
        self.text_ip.setGeometry(QtCore.QRect(80, 30, 171, 31))
        self.text_ip.setObjectName("textEdit")
        self.text_ip.setFont(font)

        self.text_port = QtWidgets.QTextEdit(Server_int)
        self.text_port.setGeometry(QtCore.QRect(80, 70, 171, 31))
        self.text_port.setObjectName("textEdit_2")
        self.text_port.setFont(font)

        self.retranslateUi(Server_int)
        QtCore.QMetaObject.connectSlotsByName(Server_int)

    def retranslateUi(self, Server_int):
        _translate = QtCore.QCoreApplication.translate
        Server_int.setWindowTitle(_translate("Server_int", "Admin"))
        self.pushButton.setText(_translate("Server_int", "Подключить"))
        self.label_ip.setText(_translate("Server_int", "IP-адрес"))
        self.label_port.setText(_translate("Server_int", "Порт"))
        self.text_port.setText(CONFIG['DEFAULT_PORT'])
        self.text_ip.setText(CONFIG['DEFAULT_IP_SERVER'])
        self.pushButton.clicked.connect(self.connect_server)

    def connect_server(self):
        # print(f'{self.text_ip.toPlainText()}\n{self.text_port.toPlainText()}')
        server_class.main(int(self.text_port.toPlainText()), self.text_ip.toPlainText())

