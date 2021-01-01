import sys

import time

from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QScrollArea, QVBoxLayout, QLineEdit, QPushButton, \
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QInputDialog, QButtonGroup, \
    QStackedLayout, QErrorMessage
from PyQt5.QtCore import Qt

from pyqtgraph import PlotWidget, AxisItem

import database

import hashcode_utils

import holdings_data_utils


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
                self.main_gui = MainGui()
                self.main_gui.show()
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

    @staticmethod
    def register(entered_username, password):
        credentials_concatenated = entered_username + ":" + password
        generated_hash = hashcode_utils.create_hash(credentials_concatenated)
        database.create_new_user(generated_hash, entered_username)


class MainGui(QWidget):
    def __init__(self):
        super().__init__()

        # Window Properties
        screen = app.primaryScreen()
        size = screen.size()
        self.title = "Portfolio"
        self.width = size.width()
        self.height = size.height()
        self.top = 0
        self.left = 0
        self.iconName = "icons/aktien_icon.png"

        size_units = {"width_unit": round(size.width()/100), "height_unit": round(size.height()/100)}

        # Set Window Properties
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
        self.label_label_credits = QLabel(self.stack_portfolio)
        self.label_browse_holdings = QLabel(self.stack_portfolio)
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
        self.label_label_holding_name = QLabel(self.stack_browse_holdings)
        self.label_company_name = QLabel(self.stack_browse_holdings)
        self.label_holding_price = QLabel(self.stack_browse_holdings)
        self.label_label_holding_price = QLabel(self.stack_browse_holdings)
        self.label_browse_new_holding = QLabel(self.stack_browse_holdings)
        self.label_credits_browse_holding = QLabel(self.stack_browse_holdings)
        self.label_label_credits_browse_holding = QLabel(self.stack_browse_holdings)
        self.textbox_browse_new_holding = QLineEdit(self.stack_browse_holdings)
        self.button_buy_holding = QPushButton(self.stack_browse_holdings)
        self.button_back_to_portfolio = QPushButton(self.stack_browse_holdings)
        self.error_message = QErrorMessage(self.stack_browse_holdings)
        # Graph
        self.layout_hold_graph_browse_holdings = QVBoxLayout(self.stack_browse_holdings)
        self.widget_hold_graph_browse_holdings = QWidget(self.stack_browse_holdings)
        self.date_axis_browse_holdings = DateAxis(orientation="bottom")
        self.graph_for_browse_holdings = PlotWidget(self.stack_browse_holdings,
                                                    axisItems={'bottom': self.date_axis_browse_holdings},
                                                    enableMenu=False, title='Holding Data')

        username = self.get_username()
        self.init_portfolio(username, size_units)
        self.init_browse_holdings(size_units)

        self.which_holdings_button = 1
        self.holdings_data = ""

        self.show()

    def init_portfolio(self, username, size_units):
        user_credits = database.get_credits_by_username(username)
        width_unit = size_units["width_unit"]
        height_unit = size_units["height_unit"]

        # Label_Credits
        self.label_label_credits.move(width_unit*8, height_unit*3)
        self.label_label_credits.setText("Credits:")
        self.label_label_credits.setFont(QFont("Arial", 50))
        self.label_credits.move(width_unit*20, height_unit*3)
        self.label_credits.setText(str(user_credits))
        self.label_credits.setFont(QFont("Arial", 50))

        # Label_Browse_Holdings
        self.label_browse_holdings.move(width_unit*75, height_unit*5)
        self.label_browse_holdings.setText("Browse holdings:")

        # TextBox_browse_holdings
        self.textbox_browse_holdings.move(width_unit*82, height_unit*5)
        self.textbox_browse_holdings.returnPressed.connect(self.change_card_to_browse_holdings)

        # Table
        self.scroll_holdings.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_holdings.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_holdings.setWidgetResizable(True)
        self.scroll_holdings.setWidget(self.table_show_all_holdings)
        self.scroll_holdings.setGeometry(width_unit*6, height_unit*50, width_unit * 88, height_unit * 50)
        self.table_first_init(username)

        # Graph
        self.layout_hold_graph_portfolio.addWidget(self.graph_for_portfolio)
        self.widget_hold_graph_portfolio.setLayout(self.layout_hold_graph_portfolio)
        self.widget_hold_graph_portfolio.setGeometry(width_unit*7, height_unit*10, width_unit*86, height_unit*40)
        first_holding = self.get_first_holding_from_user(username)
        self.update_graph(first_holding, "1Y", self.graph_for_portfolio)

    def init_browse_holdings(self, size_units):
        width_unit = size_units["width_unit"]
        height_unit = size_units["height_unit"]

        # Label_Holding_Name
        self.label_label_holding_name.move(width_unit*7, height_unit*80)
        self.label_label_holding_name.setText("Holding:")
        self.label_holding_name.move(width_unit*12, height_unit*80)

        # Label_Holding_Price
        self.label_label_holding_price.move(width_unit*7, height_unit*83)
        self.label_label_holding_price.setText("Price:")
        self.label_holding_price.move(width_unit*12, height_unit*83)

        # Label_Browse_New_Holding
        self.label_browse_new_holding.move(width_unit*75, height_unit*5)
        self.label_browse_new_holding.setText("Browse holdings:")

        # Label_Credits
        self.label_label_credits_browse_holding.move(width_unit*80, height_unit*80)
        self.label_label_credits_browse_holding.setText('Credits:')
        self.label_credits_browse_holding.move(width_unit*83, height_unit*80)

        # TextBox_Browse_New_Holding
        self.textbox_browse_new_holding.move(width_unit*82, height_unit*5)
        self.textbox_browse_new_holding.setToolTip("Browse new holding")
        self.textbox_browse_new_holding.returnPressed.connect(self.browse_new_holding)

        # Button_Buy_holding
        self.button_buy_holding.move(width_unit*80, height_unit*83)
        self.button_buy_holding.setText("Buy Holding")
        self.button_buy_holding.clicked.connect(self.buy_holding)

        # Button_Back_To_Portfolio
        self.button_back_to_portfolio.move(width_unit*7, height_unit*4)
        self.button_back_to_portfolio.setText("Back to Portfolio")
        self.button_back_to_portfolio.clicked.connect(self.change_card_to_portfolio)

        # Graph
        self.layout_hold_graph_browse_holdings.addWidget(self.graph_for_browse_holdings)
        self.widget_hold_graph_browse_holdings.setLayout(self.layout_hold_graph_browse_holdings)
        self.widget_hold_graph_browse_holdings.setGeometry(width_unit*7, height_unit*10, width_unit*86, height_unit*60)

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
        number_to_buy, is_buy_holding = self.how_many_holdings("buy")
        if is_buy_holding:
            username = self.get_username()
            holding = self.label_holding_name.text()
            holding_price = float(self.label_holding_price.text())
            holding_price = int(round(holding_price))
            user_credits = database.get_credits_by_username(username)
            if database.user_already_has_holding(username, holding):
                number_of_holdings_user_already_has = database.get_amount_of_holdings_user_already_has(username,
                                                                                                       holding)
                if user_credits > holding_price * number_to_buy:
                    old_buy_in_price = database.get_buy_in_price(username, holding)
                    number_of_total_holdings = number_of_holdings_user_already_has + number_to_buy
                    new_buy_in_price = (old_buy_in_price * number_of_holdings_user_already_has
                                        + holding_price * number_to_buy) / number_of_total_holdings
                    new_buy_in_price = round(new_buy_in_price, 2)
                    database.update_number_of_holdings(username, holding, number_of_total_holdings, new_buy_in_price)
                    new_amount_of_credits = user_credits - holding_price * number_to_buy
                    print(new_amount_of_credits)
                    database.update_credits_in_database(username, new_amount_of_credits)
                    self.label_credits_browse_holding.setText(str(new_amount_of_credits))
                    self.label_credits_browse_holding.adjustSize()
                    print("Bought Holding")
                else:
                    self.error_message.showMessage('Not enough credits')
            else:
                if user_credits > holding_price * number_to_buy:
                    database.create_new_holding(username, holding, number_to_buy, holding_price)
                    new_amount_of_credits = user_credits - holding_price * number_to_buy
                    database.update_credits_in_database(username, new_amount_of_credits)
                    print("Bought Holding")
                else:
                    self.error_message.showMessage('Not enough credits')

    def sell_holding(self, which_button_index):
        number_to_sell, is_sell_holding = self.how_many_holdings("sell")
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

    def how_many_holdings(self, action):
        if action == "buy":
            amount_of_holdings, ok_pressed = QInputDialog.getInt(self, "Buy Holdings", "Holdings to buy")
        if action == "sell":
            amount_of_holdings, ok_pressed = QInputDialog.getInt(self, "Sell Holdings", "Holdings to sell")
        if ok_pressed:
            if amount_of_holdings == 0:
                return 0, ok_pressed
            return amount_of_holdings, ok_pressed
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
        username = self.get_username()
        user_credits = database.get_credits_by_username(username)
        self.label_credits.setText(str(user_credits))
        self.label_credits.adjustSize()
        self.update_table(username)

    def change_card_to_browse_holdings(self):
        self.stack.setCurrentIndex(1)
        self.browse_holding()
        holding_to_show = self.textbox_browse_holdings.text()
        self.update_graph(holding_to_show, "1y", self.graph_for_browse_holdings)
        username = self.get_username()
        user_credits = database.get_credits_by_username(username)
        self.label_credits_browse_holding.setText(str(user_credits))
        self.label_credits_browse_holding.adjustSize()

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
            self.update_graph(holding_name, "1y", self.graph_for_browse_holdings)
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

    @staticmethod
    def get_first_holding_from_user(username):
        first_holding = database.get_holding_names_from_user(username)[0]
        return first_holding


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
    if hashcode_utils.return_hash_if_exists()[1]:
        main_gui = MainGui()
    else:
        register = Register()
    sys.exit(app.exec_())
