import sys

from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableView, QAction, qApp, QDialog, QLabel, QLineEdit, \
    QPushButton, QFileDialog

from util import CONFIG


def gui_create_model(database):
    list_users = database.active_users_list()
    list = QStandardItemModel()
    list.setHorizontalHeaderLabels(['Имя Клиента', 'IP Адрес', 'Порт', 'Время подключения'])
    for row in list_users:
        user, ip, port, time = row
        user = QStandardItem(user)
        user.setEditable(False)
        ip = QStandardItem(ip)
        ip.setEditable(False)
        port = QStandardItem(str(port))
        port.setEditable(False)
        time = QStandardItem(str(time.replace(microsecond=0)))
        time.setEditable(False)
        list.appendRow([user, ip, port, time])
    return list


class ServerInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(500, 300, 700, 500)
        self.setWindowTitle('Server Interface')

        self.statusBar()

        bar = self.menuBar()
        self.menu = bar.addMenu('Меню')

        self.refresh = QAction('Обновить список', self)
        self.refresh.setShortcut('Ctrl+U')

        self.history = QAction('История клиентов', self)

        self.exit = QAction('Выход', self)
        self.exit.setShortcut('Ctrl+Q')
        self.exit.triggered.connect(qApp.quit)

        self.menu.addAction(self.refresh)
        self.menu.addAction(self.history)
        self.menu.addAction(self.exit)

        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(10, 80)
        self.active_clients_table.setFixedSize(680, 400)

        # Метка с номером порта
        self.port_label = QLabel('Порт:', self)
        self.port_label.move(10, 25)
        self.port_label.setFixedSize(180, 15)

        # Поле для ввода номера порта
        self.port = QLineEdit(self)
        self.port.move(60, 25)
        self.port.setText(CONFIG['DEFAULT_PORT'])
        self.port.setFixedSize(150, 20)

        # Метка с адресом для соединений
        self.ip_label = QLabel('IP:', self)
        self.ip_label.move(10, 50)
        self.ip_label.setFixedSize(180, 15)

        # Поле для ввода ip
        self.ip = QLineEdit(self)
        self.ip.move(60, 50)
        self.ip.setText(CONFIG['DEFAULT_IP_SERVER'])
        self.ip.setFixedSize(150, 20)

        # Кнопка сохранения настроек
        self.connect_btn = QPushButton('Подключить', self)
        self.connect_btn.move(240, 35)

        self.show()


    def get_connect_param(self):
        return (self.port.text(), self.ip.text())




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ServerInterface()
    sys.exit(app.exec_())
