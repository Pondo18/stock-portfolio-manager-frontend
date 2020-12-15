import sys

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QScrollArea, QVBoxLayout, QSlider, QLineEdit, QPushButton, \
    QHBoxLayout, QMainWindow, QGridLayout
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets, uic

from pyqtgraph import PlotData

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
        self.label_holding = QLabel(self)
        self.label_price = QLabel(self)
        self.label_buy_in = QLabel(self)
        self.label_number = QLabel(self)
        self.label_buy_date = QLabel(self)

        """#Create Hbox_Scroll_Menu_Above
        self.hbox_scroll_menu_above = QHBoxLayout(self)"""

        # Create Scroll_Holdings
        self.scroll_holdings = QScrollArea(self)

        # Create Widget_Holdings
        self.widget_holdings = QWidget()

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

        horizontal_size_scroll_menu = size.width()-500
        horizontal_size_scroll_menu_label_distance = horizontal_size_scroll_menu/4
        distance_yet = 110
        n = size.width()/168

        self.label_holding.setText("Holding")
        self.label_holding.move(int(distance_yet), 370)
        distance_yet += horizontal_size_scroll_menu_label_distance
        self.label_price.setText("Price")
        self.label_price.move(int(distance_yet-n), 370)
        distance_yet += horizontal_size_scroll_menu_label_distance
        self.label_buy_in.setText("BuyIn Price")
        self.label_buy_in.move(int(distance_yet-n*2), 370)
        distance_yet += horizontal_size_scroll_menu_label_distance
        self.label_number.setText("Number of holdings")
        self.label_number.move(int(distance_yet-n*3), 370)
        distance_yet += horizontal_size_scroll_menu_label_distance
        self.label_buy_date.setText("Buy Date")
        self.label_buy_date.move(int(distance_yet-n*3), 370)

        # Scroll_Holdings
        self.scroll_holdings.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_holdings.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_holdings.setWidgetResizable(True)
        self.scroll_holdings.setWidget(self.widget_holdings)
        self.scroll_holdings.setGeometry(100, 400, size.width()-200, size.height()-500)

        self.show_holdings(username)

        # Widget_Holdings
        self.widget_holdings.setLayout(self.grid_holdings)

    def return_holdings_data(self, holdings):
        data_from_all_holdings = []

        for holding in holdings:
            holding_name = holding["holding"]
            holding_price = "x"
            holding_buy_in = str(holding["buyIn"])
            holding_buy_in = holding_buy_in + "€"
            holding_number = str(holding["number"])
            holding_buy_date = str(holding["buyDate"])
            holding_data = [holding_name, holding_price, holding_buy_in, holding_number, holding_buy_date]
            for data in holding_data:
                data_from_all_holdings.append(data)
        return data_from_all_holdings

    def show_holdings(self, username):
        holdings = database.get_holdings_from_user(username)
        holdings_data = self.return_holdings_data(holdings)
        amount_of_holdings = len(holdings)

        positions = [(i, j) for i in range(amount_of_holdings) for j in range(5)]
        for position, data in zip(positions, holdings_data):
            if data == '':
                continue
            label_data = QLabel(data)
            self.grid_holdings.addWidget(label_data, *position)

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
