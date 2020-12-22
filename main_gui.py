import sys

import math

import time

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QScrollArea, QVBoxLayout, QSlider, QLineEdit, QPushButton, \
    QHBoxLayout, QMainWindow, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, \
    QInputDialog, QButtonGroup
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5 import QtWidgets

from pyqtgraph import PlotData, PlotWidget, AxisItem

import database

import hashcode_utils

import holdings_data_utils


#  TODO: Dynamischee Größen


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
        # Create Scroll_Holdings
        self.scroll_holdings = QScrollArea(self)

        # Create Table_Widget
        self.table_widget = QTableWidget(self)

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

        # Create Layout_Hold_Graph_Portfolio
        self.layout_hold_graph_portfolio = QVBoxLayout(self)
        self.widget_hold_graph_portfolio = QWidget(self)

        # Create Graph_For_Portfolio
        self.date_axis = DateAxis(orientation="bottom")
        self.graph_for_portfolio = PlotWidget(self, axisItems={'bottom': self.date_axis}, enableMenu=False,
                                              title='Holding Data')

        username = self.get_username()
        self.init_me(username, size)

        self.which_holdings_button = 1

        self.holdings_data = ""

        self.show()

    def init_me(self, username, size):
        self.init_portfolio(username, size)
        self.show_browse_holdings_page(False)

    def init_portfolio(self, username, size):
        user_credits = database.get_credits_by_username(username)

        # Label_Credits
        self.label_credits.move(400, 50)
        self.label_credits.setText(str(user_credits))
        self.label_credits.setFont(QFont("Arial", 50))

        # Label_Portfolio
        self.label_portfolio.move(150, 50)
        self.label_portfolio.setText("Your Portfolio")
        self.label_portfolio.setFont(QFont("Arial", 30))

        # Scroll_Menu
        # Scroll_Holdings
        self.scroll_holdings.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_holdings.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_holdings.setWidgetResizable(True)
        self.scroll_holdings.setWidget(self.table_widget)
        self.scroll_holdings.setGeometry(100, 500, size.width() - 200, size.height() - 500)

        # Init Table
        self.table_first_init(username)

        # TextBox_browse_holdings
        self.textbox_browse_holdings.move(size.width() - 300, 50)
        self.textbox_browse_holdings.returnPressed.connect(self.change_card_to_browse_holdings)

        # Graph
        self.layout_hold_graph_portfolio.addWidget(self.graph_for_portfolio)
        self.widget_hold_graph_portfolio.setLayout(self.layout_hold_graph_portfolio)
        self.widget_hold_graph_portfolio.setGeometry(100, 100, 1460, 400)
        self.update_graph(username, "SAP", "1Y")

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

    def init_table(self, username):
        holding_names = database.get_holding_names_from_user(username)
        amount_of_holdings = len(holding_names)

        self.table_widget.setRowCount(amount_of_holdings)
        self.table_widget.setColumnCount(5)
        self.table_widget.setFont(QFont("Arial", 15))
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set Horizontal Headers
        self.table_widget.setHorizontalHeaderItem(0, QTableWidgetItem("Current price"))
        self.table_widget.setHorizontalHeaderItem(1, QTableWidgetItem("BuyIn price"))
        self.table_widget.setHorizontalHeaderItem(2, QTableWidgetItem("Amount of holdings"))
        self.table_widget.setHorizontalHeaderItem(3, QTableWidgetItem("BuyIn date"))
        self.table_widget.setHorizontalHeaderItem(4, QTableWidgetItem("Sell Holding"))
        self.table_widget.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.table_widget.horizontalHeader().setFont(QFont("Arial", 18))

        # Set Vertical Headers
        self.table_widget.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)

        for i in range(amount_of_holdings):
            self.table_widget.setVerticalHeaderItem(i, QTableWidgetItem(holding_names[i]))

        self.table_widget.clicked.connect(self.table_clicked)

    def table_clicked(self, item):
        username = self.get_username()
        holding_names = database.get_holding_names_from_user(username)
        row = item.row()
        clicked_holding_row = holding_names[row]
        self.update_graph(username, clicked_holding_row, "1y")

    def table_first_init(self, username):
        self.init_table(username)
        self.show_holdings_in_table(username)

    # TODO: an generelle Aktien anpassen

    def init_graph(self):
        holding_data = holdings_data_utils.get_holding_price_for_period("SAP", "1y")
        prices = holding_data.values
        date = holding_data.keys()
        date_in_ticks = self.date_in_ticks(date)
        self.graph_for_portfolio.plot(x=date_in_ticks, y=prices)

    def buy_holding(self):
        username = self.get_username()
        holding = self.label_holding_name.text()
        holding_price = float(self.label_holding_price.text())
        holding_price = int(round(holding_price))
        user_credits = database.get_credits_by_username(username)
        user_credits = int(round(user_credits))
        number_of_new_holdings = int(self.textbox_number_of_holdings.text())
        number_of_new_holdings = round(number_of_new_holdings)
        if not math.isnan(number_of_new_holdings):
            if database.user_already_has_holding(username, holding):
                number_of_holdings_user_already_has = database.get_amount_of_holdings_user_already_has(username,
                                                                                                       holding)
                if user_credits > holding_price * number_of_new_holdings:
                    old_buy_in_price = database.get_buy_in_price(username, holding)
                    number_of_total_holdings = number_of_holdings_user_already_has + number_of_new_holdings
                    new_buy_in_price = (old_buy_in_price * number_of_holdings_user_already_has
                                        + holding_price * number_of_new_holdings) / number_of_total_holdings
                    new_buy_in_price = round(new_buy_in_price, 2)
                    database.update_number_of_holdings(username, holding, number_of_total_holdings, new_buy_in_price)
                    database.update_credits_in_database(username, user_credits - holding_price * number_of_new_holdings)
                    print("Bought Holding")
                else:
                    print("Not enough credits")
            else:
                if user_credits > holding_price:
                    database.create_new_holding(username, holding, number_of_new_holdings, holding_price)
                    database.update_credits_in_database(username, holding_price)
                    print("Bought Holding")
                else:
                    print("Not enough credits")
        else:
            print("Please enter a valid number")

        self.update_table(username)

    def sell_holding(self, which_button_index):
        number_to_sell, is_sell_holding = self.ask_for_number_to_sell()
        if is_sell_holding:
            index_of_clicked_button = which_button_index
            username = self.get_username()
            holdings = database.get_holding_names_from_user(username)
            holding = holdings[index_of_clicked_button]
            old_user_credits = database.get_credits_by_username(username)
            old_amount_of_holdings = database.get_amount_of_holdings_user_already_has(username, holding)
            current_holding_price = holdings_data_utils.get_current_price_of_holding(holding)
            new_amount_of_credits = old_user_credits + current_holding_price * number_to_sell
            new_amount_of_holdings = old_amount_of_holdings - number_to_sell
            buy_in = database.get_buy_in_price(username, holding)

            database.update_credits_in_database(username, new_amount_of_credits)
            database.update_number_of_holdings(username, holding, new_amount_of_holdings, buy_in)

            self.update_table(username)

    def update_table(self, username):
        self.update_credits(username)
        self.table_widget.clear()
        holdings = database.get_holdings_from_user(username)
        # holdings_data_as_list = self.return_holdings_data_for_portfolio(holdings)
        self.init_table(username)
        self.show_holdings_in_table(username)

    def update_graph(self, username, holding, period):
        self.graph_for_portfolio.clear()
        self.graph_for_portfolio.setTitle(title=holding)
        holding_data = holdings_data_utils.get_holding_price_for_period(holding, period)
        prices = holding_data.values
        date = holding_data.keys()
        date_in_ticks = self.date_in_ticks(date)
        self.graph_for_portfolio.plot(x=date_in_ticks, y=prices)

    def date_in_ticks(self, dates):
        return [date.timestamp() for date in dates]

    def ask_for_number_to_sell(self):
        holdings_to_sell, ok_pressed = QInputDialog.getInt(self, "Sell Holdings", "Holdings to sell")
        if ok_pressed:
            if holdings_to_sell == 0:
                return 0, ok_pressed
            return holdings_to_sell, ok_pressed
        else:
            return 0, ok_pressed

    def buttons_to_dict(self):
        username = self.get_username()
        holdings = database.get_holding_names_from_user(username)
        buttons_from_holdings = {}
        for holding in holdings:
            button_from_holding = {holding: QPushButton(self)}
            buttons_from_holdings.update(button_from_holding)
        return buttons_from_holdings

    def change_card_to_portfolio(self):
        self.show_portfolio_page(True)
        self.show_browse_holdings_page(False)
        self.textbox_browse_holdings.clear()

    def change_card_to_browse_holdings(self):
        self.init_browse_holdings()
        self.show_portfolio_page(False)
        self.show_browse_holdings_page(True)
        self.browse_holding()

    def browse_holding(self):
        holding_name = self.textbox_browse_holdings.text()
        if holdings_data_utils.holding_exists(holding_name):
            self.label_holding_name.setText(holding_name)
            holding_price = holdings_data_utils.get_current_price_of_holding(holding_name)
            self.label_holding_price.setText(str(holding_price))
        else:
            self.label_holding_name.setText("Holding doesn't exist")
            self.button_buy_holding.setDisabled(True)

    def browse_new_holding(self):
        holding_name = self.textbox_browse_new_holding.text()
        if holdings_data_utils.holding_exists(holding_name):
            self.label_holding_name.setText(holding_name)
            holding_price = holdings_data_utils.get_current_price_of_holding(holding_name)
            self.label_holding_price.setText(str(holding_price))
            self.button_buy_holding.setEnabled(True)
        else:
            self.label_holding_name.setText("Holding doesn't exist")
            self.button_buy_holding.setDisabled(True)

    def return_holdings_data_for_portfolio(self, holdings):
        data_from_all_holdings = []

        for holding in holdings:
            holding_name = holding["holding"]
            holding_price = holdings_data_utils.get_current_price_of_holding(holding_name)
            holding_price = round(holding_price, 2)
            holding_price = str(holding_price) + "$"
            holding_buy_in = str(holding["buyIn"])
            holding_buy_in = holding_buy_in + "$"
            holding_number = str(holding["number"])
            holding_buy_date = str(holding["buyDate"])
            holding_data = [holding_price, holding_buy_in, holding_number, holding_buy_date]
            for data in holding_data:
                data_from_all_holdings.append(data)
        return data_from_all_holdings

    def show_holdings_in_table(self, username):
        holdings = database.get_holdings_from_user(username)
        holdings_data = self.return_holdings_data_for_portfolio(holdings)
        amount_of_holdings = len(holdings)

        positions = [(i, j) for i in range(amount_of_holdings) for j in range(4)]
        for position, data in zip(positions, holdings_data):
            if data == '':
                continue
            self.table_widget.setItem(position[0], position[1], QTableWidgetItem(data))
        self.show_buttons_in_table(username)

    def show_buttons_in_table(self, username):
        holdings = database.get_holding_names_from_user(username)
        buttons_as_dict = self.buttons_to_dict()
        button_index = 0
        self.button_group_sell = QButtonGroup(self)
        for holding in holdings:
            self.button = buttons_as_dict[holding]
            self.button.setText("Sell")

            self.button_group_sell.addButton(self.button)

            self.button.clicked.connect(lambda state, x=button_index: self.sell_holding(x))
            self.table_widget.setCellWidget(button_index, 4, self.button)
            button_index += 1

    def get_username(self):
        hashcode = hashcode_utils.return_hash_if_exists()
        username = database.get_username_by_hashcode(hashcode)
        return username

    def update_credits(self, username):
        user_credits = database.get_credits_by_username(username)
        self.label_credits.setText(str(user_credits))

    def show_portfolio_page(self, is_true):
        if is_true:
            # Window Properties
            # self.title("Portfolio")

            # Show Labels
            self.label_credits.show()
            self.label_portfolio.show()

            # Show Scroll_Menu
            self.scroll_holdings.show()

            # Show Table_Widget
            self.table_widget.show()

            # Show Textbox
            self.textbox_browse_holdings.show()

            self.widget_hold_graph_portfolio.show()
        else:
            # Hide Labels
            self.label_credits.hide()
            self.label_portfolio.hide()

            # Hide Scroll_Menu
            self.scroll_holdings.hide()

            # Hide Table_Widget
            self.table_widget.hide()

            # Hide Textbox
            self.textbox_browse_holdings.hide()

            self.widget_hold_graph_portfolio.hide()

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


class DateAxis(AxisItem):
    def tickStrings(self, values, scale, spacing):
        strns = []
        rng = max(values) - min(values)
        if rng < 3600 * 24:
            string = '%H:%M:%S'
            label1 = '%b %d -'
            label2 = ' %b %d, %Y'
        elif rng >= 3600 * 24 and rng < 3600 * 24 * 30:
            string = '%d'
            label1 = '%b - '
            label2 = '%b, %Y'
        elif rng >= 3600 * 24 * 30 and rng < 3600 * 24 * 30 * 24:
            string = '%b'
            label1 = '%Y -'
            label2 = ' %Y'
        elif rng >= 3600 * 24 * 30 * 24:
            string = '%Y'
            label1 = ''
            label2 = ''
        for x in values:
            try:
                strns.append(time.strftime(string, time.localtime(x)))
            except ValueError:
                strns.append('')
        try:
            label = time.strftime(label1, time.localtime(min(values))) + time.strftime(label2,
                                                                                       time.localtime(max(values)))
        except ValueError:
            label = ''
        return strns


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = main_gui()
    sys.exit(app.exec_())
