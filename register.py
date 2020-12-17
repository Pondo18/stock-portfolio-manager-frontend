import sys

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QLabel


import database

import hashcode_functions


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

        #self.icon_username = QLabel(self)

        #self.icon_password = QLabel(self)

        self.label_username_already_taken = QLabel(self)
        self.label_username_longer_than_20_chars = QLabel(self)

        self.init_me()

        self.show()

    def init_me(self):
        # TextBox_Username
        self.textbox_username.move(100, 200)
        self.textbox_username.resize(200, 20)

        # Textbox_Password
        self.textbox_password.move(100, 250)
        self.textbox_password.resize(200, 20)
        self.textbox_password.setEchoMode(QLineEdit.Password)
        self.textbox_password.returnPressed.connect(self.enter_press)

        # Icon_Username
        """self.icon_username.setPixmap("icons/man.png")
        self.icon_username.move(80, 200)

        # Icon_Password
        self.icon_password.setPixmap(QtGui.QPixmap("icons/key.png"))
        self.icon_password.move(80, 250)"""

        # Label_Username_Already_Taken
        self.label_username_already_taken.move(100, 290)
        self.label_username_already_taken.setText("Username already taken")
        self.label_username_already_taken.hide()

        # Label_Username_Longer_Than_20_chars
        self.label_username_longer_than_20_chars.move(100, 290)
        self.label_username_longer_than_20_chars.setText("Username shouldn't be longer than 20 character")
        self.label_username_longer_than_20_chars.hide()

    def enter_press(self):
        typed_in_username = self.textbox_username.text()
        length_username = len(typed_in_username)
        typed_in_password = self.textbox_password.text()
        if database.username_already_exists(typed_in_username):
            if not length_username > 20:
                self.register(typed_in_password, typed_in_password)
                self.close()
            else:
                self.label_username_longer_than_20_chars.show()
                self.textbox_password.clear()
        else:
            self.label_username_already_taken.show()
            self.textbox_password.clear()

    def register(self, username, password):
        credentials_concatenated = username + ":" + password
        hashcode = hashcode_functions.create_hash(credentials_concatenated)
        database.create_new_user(hashcode, username)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    if hashcode_functions.return_hash_if_exists()[1]:
        hashcode = hashcode_functions.return_hash_if_exists()
        username = database.get_username_by_hashcode(hashcode)
        database.get_credits_by_username(username)
    else:
        window = Register()
    sys.exit(app.exec_())
