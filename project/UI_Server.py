import sys

from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableView, QAction, qApp



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
        self.active_clients_table.move(10, 45)
        self.active_clients_table.setFixedSize(680, 400)

        self.show()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ServerInterface()
    sys.exit(app.exec_())
