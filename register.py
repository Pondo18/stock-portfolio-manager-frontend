import sys

import start

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QToolTip, QLineEdit
from PyQt5.QtCore import Qt


class Register(QWidget):
    def __init__(self):
        super().__init__()

        screen = app.primaryScreen()
        size = screen.size()
        self.title = "Register"
        self.width = 500
        self.height = 600
        self.top = round((size.height() - self.height) / 2)
        self.left = round((size.width() - self.width) / 2)
        self.iconName = "icons/aktien_icon.png"

        self.setWindowIcon(QIcon(self.iconName))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.textbox_username = QLineEdit(self)

        self.textbox_password = QLineEdit(self)

        self.init_me()

        self.show()

    def init_me(self):
        #self.textbox_username = QLineEdit(self)
        self.textbox_username.move(100, 200)
        self.textbox_username.resize(200, 20)

        #self.textbox_password = QLineEdit(self)
        self.textbox_password.move(100, 250)
        self.textbox_password.resize(200, 20)
        self.textbox_password.setEchoMode(QLineEdit.Password)
        self.textbox_password.returnPressed.connect(self.enter_press)



    def enter_press(self):
        start.login(self.textbox_username.text(), self.textbox_password.text())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Register()
    sys.exit(app.exec_())
