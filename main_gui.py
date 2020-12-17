import sys

import math

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QScrollArea, QVBoxLayout, QSlider, QLineEdit, QPushButton, \
    QHBoxLayout, QMainWindow, QGridLayout
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets, uic

from pyqtgraph import PlotData

import database

import hashcode_functions

import holdings_data


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

        # Portfolio_page
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

        # Create Scroll_Holdings
        self.scroll_holdings = QScrollArea(self)

        # Create Widget_Holdings
        self.widget_holdings = QWidget()

        # Create Grid_Holdings
        self.grid_holdings = QGridLayout()

        # Create TextBox_browse_holdings
        self.textbox_browse_holdings = QLineEdit(self)

        # Browse_Holdings_Page
        # Create TextBox_Browse_New_Holding
        self.textbox_browse_new_holding = QLineEdit(self)

        # Create TextBox_Number_Of_Holdings
        self.textbox_number_of_holdings = QLineEdit(self)

        # Create Label_Holding_Name
        self.label_holding_name = QLabel(self)

        # Create Button_Buy_Holding
        self.button_buy_holding = QPushButton(self)

        # Create Button_Back_To_Portfolio
        self.button_back_to_portfolio = QPushButton(self)

        # Create Label_Holding_Price
        self.label_holding_price = QLabel(self)

        username = self.get_username()
        self.init_me(username, size)

        self.show()

    def init_me(self, username, size):
        self.init_portfolio(username, size)
        self.show_browse_holdings_page(False)

    def init_portfolio(self, username, size):
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

        horizontal_size_scroll_menu = size.width() - 500
        horizontal_size_scroll_menu_label_distance = horizontal_size_scroll_menu / 4
        distance_yet = 110
        n = size.width() / 168

        self.label_holding.setText("Holding")
        self.label_holding.move(int(distance_yet), 370)
        distance_yet += horizontal_size_scroll_menu_label_distance
        self.label_price.setText("Price")
        self.label_price.move(int(distance_yet - n), 370)
        distance_yet += horizontal_size_scroll_menu_label_distance
        self.label_buy_in.setText("BuyIn Price")
        self.label_buy_in.move(int(distance_yet - n * 2), 370)
        distance_yet += horizontal_size_scroll_menu_label_distance
        self.label_number.setText("Number of holdings")
        self.label_number.move(int(distance_yet - n * 3), 370)
        distance_yet += horizontal_size_scroll_menu_label_distance
        self.label_buy_date.setText("Buy Date")
        self.label_buy_date.move(int(distance_yet - n * 3), 370)

        # Scroll_Holdings
        self.scroll_holdings.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_holdings.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_holdings.setWidgetResizable(True)
        self.scroll_holdings.setWidget(self.widget_holdings)
        self.scroll_holdings.setGeometry(100, 400, size.width() - 200, size.height() - 500)

        self.show_holdings_in_grid(username)

        # Widget_Holdings
        self.widget_holdings.setLayout(self.grid_holdings)

        # TextBox_browse_holdings
        self.textbox_browse_holdings.move(size.width()-300, 200)
        self.textbox_browse_holdings.returnPressed.connect(self.change_card_to_browse_holdings)

    def init_browse_holdings(self):
        self.textbox_browse_new_holding.move(100, 200)
        self.textbox_browse_holdings.setToolTip("Browse new holding")
        self.textbox_browse_new_holding.returnPressed.connect(self.browse_new_holding)

        self.label_holding_name.move(500, 500)

        self.button_buy_holding.move(600, 300)
        self.button_buy_holding.setText("Buy Holding")
        self.button_buy_holding.clicked.connect(self.buy_holding)

        self.button_back_to_portfolio.move(100, 100)
        self.button_back_to_portfolio.setText("Back to Portfolio")
        self.button_back_to_portfolio.clicked.connect(self.change_card_to_portfolio)

        self.label_holding_price.move(500, 300)

        self.textbox_number_of_holdings.move(300, 300)
        self.textbox_number_of_holdings.setToolTip("Number of holdings you want to buy")

    def buy_holding(self):
        username = self.get_username()
        holding = self.label_holding_name.text()
        holding_price = float(self.label_holding_price.text())
        holding_price = int(round(holding_price))
        user_credits = float(self.label_credits.text())
        user_credits = int(round(user_credits))
        number_of_new_holdings = int(self.textbox_number_of_holdings.text())
        number_of_new_holdings = round(number_of_new_holdings)
        if not math.isnan(number_of_new_holdings):
            if database.user_already_has_holding(username, holding):
                number_of_holdings_user_already_has = database.amount_of_holdings_user_already_has(username, holding)
                if user_credits > holding_price * number_of_new_holdings:
                    old_buy_in_price = database.get_buy_in_price(username, holding)
                    number_of_total_holdings = number_of_holdings_user_already_has + number_of_new_holdings
                    new_buy_in_price = (old_buy_in_price * number_of_holdings_user_already_has
                                        + holding_price * number_of_new_holdings) / number_of_total_holdings
                    new_buy_in_price = round(new_buy_in_price, 2)
                    database.change_number_of_holdings(username, holding, number_of_total_holdings, new_buy_in_price)
                    database.change_credits(username, user_credits-holding_price*number_of_new_holdings)
                    print("Bought Holding")
                else:
                    print("Not enough credits")
            else:
                if user_credits > holding_price:
                    database.create_new_holding(username, holding,  number_of_new_holdings, holding_price)
                    database.change_credits(username, holding_price)
                    print("Bought Holding")
                else:
                    print("Not enough credits")
        else:
            print("Please enter a valid number")

    def change_card_to_portfolio(self):
        self.show_portfolio_page(True)
        self.show_browse_holdings_page(False)


    def change_card_to_browse_holdings(self):
        self.init_browse_holdings()
        self.show_portfolio_page(False)
        self.show_browse_holdings_page(True)
        self.browse_holding()

    def browse_holding(self):
        holding_name = self.textbox_browse_holdings.text()
        if holdings_data.holding_exists(holding_name):
            self.label_holding_name.setText(holding_name)
            holding_price = holdings_data.get_price_of_holding(holding_name)
            self.label_holding_price.setText(str(holding_price))
        else:
            self.label_holding_name.setText("Holding doesn't exist")
            self.button_buy_holding.setDisabled(True)

    def browse_new_holding(self):
        holding_name = self.textbox_browse_new_holding.text()
        if holdings_data.holding_exists(holding_name):
            self.label_holding_name.setText(holding_name)
            holding_price = holdings_data.get_price_of_holding(holding_name)
            self.label_holding_price.setText(str(holding_price))
            self.button_buy_holding.setEnabled(True)
        else:
            self.label_holding_name.setText("Holding doesn't exist")
            self.button_buy_holding.setDisabled(True)

    def return_holdings_data_for_portfolio(self, holdings):
        data_from_all_holdings = []

        for holding in holdings:
            holding_name = holding["holding"]
            holding_price = holdings_data.get_price_of_holding(holding_name)
            holding_price = round(holding_price, 2)
            holding_price = str(holding_price) + "$"
            holding_buy_in = str(holding["buyIn"])
            holding_buy_in = holding_buy_in + "$"
            holding_number = str(holding["number"])
            holding_buy_date = str(holding["buyDate"])
            holding_data = [holding_name, holding_price, holding_buy_in, holding_number, holding_buy_date]
            for data in holding_data:
                data_from_all_holdings.append(data)
        return data_from_all_holdings

    def show_holdings_in_grid(self, username):
        holdings = database.get_holdings_from_user(username)
        holdings_data = self.return_holdings_data_for_portfolio(holdings)
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

    def show_portfolio_page(self, is_true):
        if is_true:
            # Window Properties
            #self.title("Portfolio")

            # Show Labels
            self.label_credits.show()
            self.label_portfolio.show()
            self.label_holding.show()
            self.label_price.show()
            self.label_buy_in.show()
            self.label_number.show()
            self.label_buy_date.show()

            # Show Scroll_Menu
            self.scroll_holdings.show()

            # Show Widget
            self.widget_holdings.show()

            # Show Textbox
            self.textbox_browse_holdings.show()
        else:
            # Hide Labels
            self.label_credits.hide()
            self.label_portfolio.hide()
            self.label_holding.hide()
            self.label_price.hide()
            self.label_buy_in.hide()
            self.label_number.hide()
            self.label_buy_date.hide()

            # Hide Scroll_Menu
            self.scroll_holdings.hide()

            # Hide Widget
            self.widget_holdings.hide()

            # Hide Textbox
            self.textbox_browse_holdings.hide()

    def show_browse_holdings_page(self, is_true):
        if is_true:
            self.textbox_browse_new_holding.show()
            self.textbox_number_of_holdings.show()
            self.label_holding_name.show()
            self.button_buy_holding.show()
            self.button_back_to_portfolio.show()
            self.label_holding_price.show()
        else:
            self.textbox_browse_new_holding.hide()
            self.textbox_number_of_holdings.hide()
            self.label_holding_name.hide()
            self.button_buy_holding.hide()
            self.button_back_to_portfolio.hide()
            self.label_holding_price.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = main_gui()
    sys.exit(app.exec_())
