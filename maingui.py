import sys

import math

import time

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QScrollArea, QVBoxLayout, QLineEdit, QPushButton, \
                            QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QInputDialog, QButtonGroup,\
                            QStackedLayout
from PyQt5.QtCore import Qt

from pyqtgraph import PlotWidget, AxisItem

import database

import hashcode_utils

import holdings_data_utils


#  TODO: Dynamic size


class MainGui(QWidget):
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

        # Stack
        self.stack = QStackedLayout(self)
        self.stack_portfolio = QWidget(self)
        self.stack_browse_holdings = QWidget(self)
        self.stack.addWidget(self.stack_portfolio)
        self.stack.addWidget(self.stack_browse_holdings)

        # Portfolio_page
        self.label_credits = QLabel(self.stack_portfolio)
        self.label_portfolio = QLabel(self.stack_portfolio)
        self.textbox_browse_holdings = QLineEdit(self.stack_portfolio)
        # Table
        self.scroll_holdings = QScrollArea(self.stack_portfolio)
        self.table_show_all_holdings = QTableWidget(self.stack_portfolio)
        self.button_group_sell = QButtonGroup(self)
        # Graph
        self.layout_hold_graph_portfolio = QVBoxLayout(self.stack_portfolio)
        self.widget_hold_graph_portfolio = QWidget(self.stack_portfolio)
        self.date_axis_portfolio = DateAxis(orientation="bottom")
        self.graph_for_portfolio = PlotWidget(self.stack_portfolio, axisItems={'bottom': self.date_axis_portfolio},
                                              enableMenu=False, title='Holding Data')

        # Browse_Holdings_Page
        self.label_holding_name = QLabel(self.stack_browse_holdings)
        self.label_holding_price = QLabel(self.stack_browse_holdings)
        self.textbox_browse_new_holding = QLineEdit(self.stack_browse_holdings)
        self.textbox_number_of_holdings = QLineEdit(self.stack_browse_holdings)
        self.button_buy_holding = QPushButton(self.stack_browse_holdings)
        self.button_back_to_portfolio = QPushButton(self.stack_browse_holdings)
        # Graph
        self.layout_hold_graph_browse_holdings = QVBoxLayout(self.stack_browse_holdings)
        self.widget_hold_graph_browse_holdings = QWidget(self.stack_browse_holdings)
        self.date_axis_browse_holdings = DateAxis(orientation="bottom")
        self.graph_for_browse_holdings = PlotWidget(self.stack_browse_holdings,
                                                    axisItems={'bottom': self.date_axis_browse_holdings},
                                                    enableMenu=False, title='Holding Data')

        username = self.get_username()
        self.init_portfolio(username, size)
        self.init_browse_holdings(size)

        self.which_holdings_button = 1
        self.holdings_data = ""

        self.show()

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

        # TextBox_browse_holdings
        self.textbox_browse_holdings.move(size.width() - 300, 50)
        self.textbox_browse_holdings.returnPressed.connect(self.change_card_to_browse_holdings)

        # Table
        self.scroll_holdings.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_holdings.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_holdings.setWidgetResizable(True)
        self.scroll_holdings.setWidget(self.table_show_all_holdings)
        self.scroll_holdings.setGeometry(100, 500, size.width() - 200, size.height() - 500)
        self.table_first_init(username)

        # Graph
        self.layout_hold_graph_portfolio.addWidget(self.graph_for_portfolio)
        self.widget_hold_graph_portfolio.setLayout(self.layout_hold_graph_portfolio)
        self.widget_hold_graph_portfolio.setGeometry(100, 100, 1460, 400)
        self.update_graph("SAP", "1Y", self.graph_for_portfolio)

    def init_browse_holdings(self, size):
        # TextBox_Browse_New_Holding
        self.textbox_browse_new_holding.move(600, 50)
        self.textbox_browse_new_holding.setToolTip("Browse new holding")
        self.textbox_browse_new_holding.returnPressed.connect(self.browse_new_holding)

        # Label_Holding_Name
        screen_width = size.width()
        label_holding_name_width = self.label_holding_name.width()
        print(screen_width)
        print(label_holding_name_width)
        self.label_holding_name.move(round((screen_width - label_holding_name_width)/2), 50)

        # Button_Buy_holding
        self.button_buy_holding.move(600, 500)
        self.button_buy_holding.setText("Buy Holding")
        self.button_buy_holding.clicked.connect(self.buy_holding)

        # Button_Back_To_Portfolio
        self.button_back_to_portfolio.move(100, 50)
        self.button_back_to_portfolio.setText("Back to Portfolio")
        self.button_back_to_portfolio.clicked.connect(self.change_card_to_portfolio)

        # Label_Holding_Price
        self.label_holding_price.move(300, 50)

        # Textbox_Number_Of_Holdings
        self.textbox_number_of_holdings.move(200, 50)
        self.textbox_number_of_holdings.setToolTip("Number of holdings you want to buy")

        # Graph
        self.layout_hold_graph_browse_holdings.addWidget(self.graph_for_browse_holdings)
        self.widget_hold_graph_browse_holdings.setLayout(self.layout_hold_graph_browse_holdings)
        self.widget_hold_graph_browse_holdings.setGeometry(100, 100, 1460, 400)

    def init_table(self, username):
        holding_names = database.get_holding_names_from_user(username)
        amount_of_holdings = len(holding_names)

        self.table_show_all_holdings.setRowCount(amount_of_holdings)
        self.table_show_all_holdings.setColumnCount(5)
        self.table_show_all_holdings.setFont(QFont("Arial", 15))
        self.table_show_all_holdings.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set Horizontal Headers
        self.table_show_all_holdings.setHorizontalHeaderItem(0, QTableWidgetItem("Current price"))
        self.table_show_all_holdings.setHorizontalHeaderItem(1, QTableWidgetItem("BuyIn price"))
        self.table_show_all_holdings.setHorizontalHeaderItem(2, QTableWidgetItem("Amount of holdings"))
        self.table_show_all_holdings.setHorizontalHeaderItem(3, QTableWidgetItem("BuyIn date"))
        self.table_show_all_holdings.setHorizontalHeaderItem(4, QTableWidgetItem("Sell Holding"))
        self.table_show_all_holdings.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.table_show_all_holdings.horizontalHeader().setFont(QFont("Arial", 18))

        # Set Vertical Headers
        self.table_show_all_holdings.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)

        for i in range(amount_of_holdings):
            self.table_show_all_holdings.setVerticalHeaderItem(i, QTableWidgetItem(holding_names[i]))

        self.table_show_all_holdings.clicked.connect(self.table_clicked)

    def table_clicked(self, item):
        username = self.get_username()
        holding_names = database.get_holding_names_from_user(username)
        row = item.row()
        clicked_holding_row = holding_names[row]
        self.update_graph(clicked_holding_row, "1y", self.graph_for_portfolio)

    def table_first_init(self, username):
        self.init_table(username)
        self.show_holdings_in_table(username)

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
        self.table_show_all_holdings.clear()
        self.init_table(username)
        self.show_holdings_in_table(username)

    def update_graph(self, holding, period, graph):
        graph.clear()
        graph.setTitle(title=holding)
        holding_data = holdings_data_utils.get_holding_price_for_period(holding, period)
        prices = holding_data.values
        date = holding_data.keys()
        date_in_ticks = self.date_in_ticks(date)
        graph.plot(x=date_in_ticks, y=prices)

    @staticmethod
    def date_in_ticks(dates):
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
        self.stack.setCurrentIndex(0)
        self.textbox_browse_holdings.clear()

    def change_card_to_browse_holdings(self):
        self.stack.setCurrentIndex(1)
        self.browse_holding()
        holding_to_show = self.textbox_browse_holdings.text()
        self.update_graph(holding_to_show, "1y", self.graph_for_browse_holdings)

    def browse_holding(self):
        holding_name = self.textbox_browse_holdings.text()
        if holdings_data_utils.holding_exists(holding_name):
            self.label_holding_name.setText(holding_name)
            self.label_holding_name.adjustSize()
            holding_price = holdings_data_utils.get_current_price_of_holding(holding_name)
            self.label_holding_price.setText(str(holding_price))
            self.label_holding_price.adjustSize()
        else:
            self.label_holding_name.setText("Holding doesn't exist")
            self.label_holding_name.adjustSize()
            self.button_buy_holding.setDisabled(True)

    def browse_new_holding(self):
        holding_name = self.textbox_browse_new_holding.text()
        if holdings_data_utils.holding_exists(holding_name):
            self.label_holding_name.setText(holding_name)
            self.label_holding_name.adjustSize()
            holding_price = holdings_data_utils.get_current_price_of_holding(holding_name)
            self.label_holding_price.setText(str(holding_price))
            self.label_holding_price.adjustSize()
            self.button_buy_holding.setEnabled(True)
        else:
            self.label_holding_name.setText("Holding doesn't exist")
            self.label_holding_name.adjustSize()
            self.button_buy_holding.setDisabled(True)

    @staticmethod
    def get_holdings_data_for_portfolio(holdings):
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
        holdings_data = self.get_holdings_data_for_portfolio(holdings)
        amount_of_holdings = len(holdings)

        positions = [(i, j) for i in range(amount_of_holdings) for j in range(4)]
        for position, data in zip(positions, holdings_data):
            if data == '':
                continue
            self.table_show_all_holdings.setItem(position[0], position[1], QTableWidgetItem(data))
        self.show_buttons_in_table(username)

    def show_buttons_in_table(self, username):
        holdings = database.get_holding_names_from_user(username)
        buttons_as_dict = self.buttons_to_dict()
        button_index = 0
        for holding in holdings:
            self.button = buttons_as_dict[holding]
            self.button.setText("Sell")

            self.button_group_sell.addButton(self.button)

            self.button.clicked.connect(lambda state, x=button_index: self.sell_holding(x))
            self.table_show_all_holdings.setCellWidget(button_index, 4, self.button)
            button_index += 1

    @staticmethod
    def get_username():
        hashcode = hashcode_utils.return_hash_if_exists()
        username = database.get_username_by_hashcode(hashcode)
        return username

    def update_credits(self, username):
        user_credits = database.get_credits_by_username(username)
        self.label_credits.setText(str(user_credits))


class DateAxis(AxisItem):
    def tickStrings(self, values, scale, spacing):
        strns = []
        rng = max(values) - min(values)
        if rng < 3600 * 24:
            string = '%H:%M:%S'
            label1 = '%b %d -'
            label2 = ' %b %d, %Y'
        elif 3600 * 24 <= rng < 3600 * 24 * 30:
            string = '%d'
            label1 = '%b - '
            label2 = '%b, %Y'
        elif 3600 * 24 * 30 <= rng < 3600 * 24 * 30 * 24:
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
    window = MainGui()
    sys.exit(app.exec_())
