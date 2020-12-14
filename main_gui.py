import sys

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QScrollArea, QVBoxLayout, QSlider, QLineEdit, QPushButton, \
    QHBoxLayout, QMainWindow, QGridLayout

from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets, uic

import database

import hashcode_functions


class main_gui(QWidget):
    def __init__(self):
        super().__init__()

        # Window properties
        screen = app.primaryScreen()
        size = screen.size()
        self.title = "Portfolio"
        self.width = size.width()
        self.height = size.height()
        self.top = 0
        self.left = 0
        self.iconName = "icons/aktien_icon.png"

        # Set window properties
        self.setWindowIcon(QIcon(self.iconName))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create Label_Credits
        self.label_credits = QLabel(self)

        # Create Label_Portfolio
        self.label_portfolio = QLabel(self)

        # Scroll_Menu

        # Create Label_Scroll_Menu_Above
        self.label_scroll_men_above = QLabel(self)

        # Create Scroll_Holdings
        self.scroll_holdings = QScrollArea(self)

        # Create Widget_Holdings
        self.widget_holdings = QWidget()

        """# Create VBox_Holdings
        self.vbox_holdings = QVBoxLayout()

        # Create HBox_Holdings_Test
        self.holding_one = QHBoxLayout()
        self.holding_two = QHBoxLayout()"""

        # Create Grid_Holdings
        self.grid_holdings = QGridLayout()

        username = self.get_username()
        self.init_me(username, size)

        self.show()

    def init_me(self, username, size):
        user_credits = database.get_credits_by_username(username)

        # Label_Credits
        self.label_credits.move(400, 100)
        self.label_credits.setText(str(user_credits))
        self.label_credits.setFont(QFont("Arial", 50))

        # Label_Portfolio
        self.label_portfolio.move(150, 250)
        self.label_portfolio.setText("Your Portfolio")
        self.label_portfolio.setFont(QFont("Arial", 30))

        # Scroll_Menu

        self.label_scroll_men_above.move(100, 370)
        self.label_scroll_men_above.setText("Text")

        # Scroll_Holdings
        self.scroll_holdings.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_holdings.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_holdings.setWidgetResizable(True)
        self.scroll_holdings.setWidget(self.widget_holdings)
        self.scroll_holdings.setGeometry(100, 400, size.width()-200, size.height()-500)

        holdings = database.get_holdings_from_user(username)
        amount_of_holdings = len(holdings)

        data_from_all_holdings = []

        for holding in holdings:
            holding_name = holding["holding"]
            holding_price = "x"
            #holding_buy_in = holding["buyIn"]
            holding_number = str(holding["number"])
            #holding_buy_date = holding["buyDate"]
            holding_data = [holding_name, holding_price, holding_number]
            for data in holding_data:
                data_from_all_holdings.append(data)

        positions = [(i, j) for i in range(amount_of_holdings) for j in range(3)]

        print(data_from_all_holdings)
        for position, data in zip(positions, data_from_all_holdings):
            #print(data)
            if data == '':
                continue
            label_data = QLabel(data)
            self.grid_holdings.addWidget(label_data, *position)

        """buy_in_one = QLabel(str(12))
        date_one = QLabel("date")
        self.holding_one.addWidget(buy_in_one)
        self.holding_one.addWidget(date_one)

        buy_in_two = QLabel(str(30))
        date_two = QLabel("date_two")
        self.holding_two.addWidget(buy_in_two)
        self.holding_two.addWidget(date_two)

        self.vbox_holdings.addLayout(self.holding_one)
        self.vbox_holdings.addLayout(self.holding_two)"""

        """for holding in holdings:
            new_holding = QLabel("Test")
            self.vbox_holdings.addLayout(self.hbox_single_price)"""



        # Widget_Holdings
        self.widget_holdings.setLayout(self.grid_holdings)

        self.show_holdings(username)

    def show_holdings(self, username):
        all_holdings_from_user = database.get_holdings_from_user(username)
        print(all_holdings_from_user)

    def get_username(self):
        hashcode = hashcode_functions.return_hash_if_exists()
        username = database.get_username_by_hashcode(hashcode)
        return username

    def credits_aktualisieren(self, username):
        user_credits = database.get_credits_by_username(username)
        self.label_credits.setText(str(user_credits))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = main_gui()
    sys.exit(app.exec_())
