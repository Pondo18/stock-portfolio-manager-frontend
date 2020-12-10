import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QIcon
app = QApplication(sys.argv)

w = QWidget()
w.setGeometry(250, 250, 700, 700)
w.setWindowTitle("Login")
w.setWindowIcon(QIcon("icons/aktien_icon.png"))
w.show()

sys.exit(app.exec_())