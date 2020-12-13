import sys

from PyQt5.QtWidgets import QApplication

from register import Register
import start
import hashlib
import database
from pathlib import Path

def get_hash():
    token_file = open("token.txt", "r")
    return token_file.read().rstrip()

def is_hash():
    file_path = Path("/Users/moritz.moser/Documents/HDBW/1.Semester/Python/Aktien/token.txt")
    return file_path.exists()

def when_app_started():
    if not is_hash():
        hashcode = get_hash()
        username = database.get_username_by_hashcode(hashcode)
        database.synchro(username)
    app = QApplication(sys.argv)
    register = Register(app)
    username = register.textbox_username.text()
    password = register.textbox_password.text()
    print(username)
    sys.exit(app.exec_())
    print(register.get_credentials())

#def do_register():


if __name__ == "__main__":
    when_app_started()