import sys

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QLabel


import database

import hashcode_utils


class Register(QWidget):
    def __init__(self):
        super().__init__()

        # Window Properties
        screen = app.primaryScreen()
        size = screen.size()
        self.title = "Register"
        self.width = 500
        self.height = 600
        self.top = round((size.height() - self.height) / 2)
        self.left = round((size.width() - self.width) / 2)
        self.iconName = "icons/aktien_icon.png"

        # Set Window Properties
        self.setWindowIcon(QIcon(self.iconName))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.textbox_username = QLineEdit(self)
        self.textbox_password = QLineEdit(self)
        self.pixmap_username = QPixmap('icons/man.png')
        self.pixmap_password = QPixmap('icons/key.png')
        self.label_hold_username_icon = QLabel(self)
        self.label_hold_password_icon = QLabel(self)
        self.label_error = QLabel(self)
        self.label_username_longer_than_20_chars = QLabel(self)

        self.init_me()

        self.show()

    def init_me(self):
        # TextBox_Username
        self.textbox_username.move(150, 200)
        self.textbox_username.resize(200, 20)

        # Textbox_Password
        self.textbox_password.move(150, 250)
        self.textbox_password.resize(200, 20)
        self.textbox_password.setEchoMode(QLineEdit.Password)
        self.textbox_password.returnPressed.connect(self.enter_press)

        # Icons
        self.label_hold_username_icon.setPixmap(self.pixmap_username.scaledToWidth(30))
        self.label_hold_username_icon.move(110, 190)
        self.label_hold_password_icon.setPixmap(self.pixmap_password.scaledToWidth(30))
        self.label_hold_password_icon.move(110, 245)

        # Label_Error
        self.label_error.move(200, 290)
        self.label_error.hide()

    def enter_press(self):
        typed_in_username = self.textbox_username.text()
        length_username = len(typed_in_username)
        typed_in_password = self.textbox_password.text()
        if not database.username_already_exists(typed_in_username):
            if not length_username > 20:
                self.register(typed_in_password, typed_in_password)
                self.close()
            else:
                self.label_error.setText("Username shouldn't be longer than 20 characters")
                self.label_error.adjustSize()
                self.label_error.show()
                self.textbox_password.clear()
        else:
            self.label_error.setText("Username already taken")
            self.label_error.adjustSize()
            self.label_error.show()
            self.textbox_password.clear()

    def register(self, username, password):
        credentials_concatenated = username + ":" + password
        hashcode = hashcode_utils.create_hash(credentials_concatenated)
        database.create_new_user(hashcode, username)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    if hashcode_utils.return_hash_if_exists()[1]:
        hashcode = hashcode_utils.return_hash_if_exists()
        username = database.get_username_by_hashcode(hashcode)
        database.get_credits_by_username(username)
    else:
        window = Register()
    sys.exit(app.exec_())
