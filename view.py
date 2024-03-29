import time

from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor
from PyQt5.QtWidgets import QWidget, QLabel, QScrollArea, QVBoxLayout, QLineEdit, QPushButton, \
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QInputDialog, QButtonGroup, \
    QStackedLayout, QErrorMessage, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QModelIndex

from pyqtgraph import PlotWidget, AxisItem, mkPen


class Register(QWidget):
    enter_pressed = pyqtSignal()

    def __init__(self, size):
        super(Register, self).__init__()
        # Window Properties
        self.title = "Register"
        self.width = 500
        self.height = 600
        self.top = round((size.height() - self.height) / 2)
        self.left = round((size.width() - self.width) / 2)
        self.iconName = "icons/aktien_icon.png"
        self.holding_names = ''

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

    def init_me(self):
        # TextBox_Username
        self.textbox_username.move(150, 200)
        self.textbox_username.resize(200, 20)

        # Textbox_Password
        self.textbox_password.move(150, 250)
        self.textbox_password.resize(200, 20)
        self.textbox_password.setEchoMode(QLineEdit.Password)
        self.textbox_password.returnPressed.connect(self.enter_pressed)

        # Icons
        self.label_hold_username_icon.setPixmap(self.pixmap_username.scaledToWidth(30))
        self.label_hold_username_icon.move(110, 190)
        self.label_hold_password_icon.setPixmap(self.pixmap_password.scaledToWidth(30))
        self.label_hold_password_icon.move(110, 245)

        # Label_Error
        self.label_error.move(150, 290)
        self.label_error.hide()

    def error(self, error):
        self.label_error.setText(error)
        self.label_error.adjustSize()
        self.label_error.show()
        self.textbox_password.clear()


class MainGui(QWidget):
    signal_table_clicked = pyqtSignal(QModelIndex)
    signal_buy_holding = pyqtSignal()
    signal_sell_holding = pyqtSignal()
    signal_change_to_portfolio = pyqtSignal()
    signal_change_to_browse_holdings = pyqtSignal()
    signal_browse_new_holding = pyqtSignal()
    signal_period_max = pyqtSignal()
    signal_period_year = pyqtSignal()
    signal_period_month = pyqtSignal()

    def __init__(self, size):
        super().__init__()

        # Window Properties
        self.title = "Portfolio"
        self.width = size.width()
        self.height = size.height()
        self.top = 0
        self.left = 0
        self.iconName = "icons/aktien_icon.png"

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
        self.label_account_value = QLabel(self.stack_portfolio)
        self.label_label_account_value = QLabel(self.stack_portfolio)
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
        self.label_ratio_in_period = QLabel(self.stack_browse_holdings)
        self.label_label_price_start_of_period = QLabel(self.stack_browse_holdings)
        self.label_price_start_of_period = QLabel(self.stack_browse_holdings)
        self.textbox_browse_new_holding = QLineEdit(self.stack_browse_holdings)
        self.button_buy_holding = QPushButton(self.stack_browse_holdings)
        self.button_back_to_portfolio = QPushButton(self.stack_browse_holdings)
        self.button_period_max = QPushButton(self.stack_browse_holdings)
        self.button_period_year = QPushButton(self.stack_browse_holdings)
        self.button_period_month = QPushButton(self.stack_browse_holdings)
        self.error_message = QErrorMessage(self.stack_browse_holdings)
        # Graph
        self.layout_hold_graph_browse_holdings = QVBoxLayout(self.stack_browse_holdings)
        self.widget_hold_graph_browse_holdings = QWidget(self.stack_browse_holdings)
        self.date_axis_browse_holdings = DateAxis(orientation="bottom")
        self.graph_for_browse_holdings = PlotWidget(self.stack_browse_holdings,
                                                    axisItems={'bottom': self.date_axis_browse_holdings},
                                                    enableMenu=False, title='Holding Data')

        self.holdings_data = ""

    def init_portfolio(self, size_units, user_credits):
        width_unit = size_units["width_unit"]
        height_unit = size_units["height_unit"]

        # Label_Credits
        self.label_label_credits.move(width_unit*8, height_unit*2)
        self.label_label_credits.setText("Credits:")
        self.label_label_credits.setFont(QFont("Arial", 30))
        self.label_label_credits.adjustSize()
        self.label_credits.move(width_unit*14.5, height_unit*2)
        self.label_credits.setText(str(user_credits))
        self.label_credits.setFont(QFont("Arial", 30))
        self.label_credits.adjustSize()

        # Label_Account_Value
        self.label_label_account_value.move(width_unit*8, height_unit*7)
        self.label_label_account_value.setText("Account value:")
        self.label_label_account_value.setFont(QFont("Arial", 24))
        self.label_label_account_value.adjustSize()
        self.label_account_value.move(width_unit*17.5, height_unit*7)
        self.label_account_value.setText("")
        self.label_account_value.setFont(QFont("Arial", 24))

        # Label_Browse_Holdings
        self.label_browse_holdings.move(width_unit*75, height_unit*5)
        self.label_browse_holdings.setText("Browse holdings:")

        # TextBox_browse_holdings
        self.textbox_browse_holdings.move(width_unit*82, height_unit*5)
        self.textbox_browse_new_holding.adjustSize()
        self.textbox_browse_holdings.returnPressed.connect(self.signal_change_to_browse_holdings)

        # Table
        self.scroll_holdings.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_holdings.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_holdings.setWidgetResizable(True)
        self.scroll_holdings.setWidget(self.table_show_all_holdings)
        self.scroll_holdings.setGeometry(width_unit*6, height_unit*50, width_unit * 88, height_unit * 50)

        # Graph
        self.layout_hold_graph_portfolio.addWidget(self.graph_for_portfolio)
        self.widget_hold_graph_portfolio.setLayout(self.layout_hold_graph_portfolio)
        self.widget_hold_graph_portfolio.setGeometry(width_unit*7, height_unit*10, width_unit*86, height_unit*40)
        self.graph_for_portfolio.setMouseEnabled(x=False, y=False)

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

        # Label_Price_Start of Period
        self.label_label_price_start_of_period.move(width_unit * 7, height_unit * 86)
        self.label_label_price_start_of_period.setText("Start Price")
        self.label_price_start_of_period.move(width_unit * 12, height_unit * 86)

        # Label_Ratio_In_period
        self.label_ratio_in_period.move(width_unit*7, height_unit*89)

        # Label_Browse_New_Holding
        self.label_browse_new_holding.move(width_unit*75, height_unit*5)
        self.label_browse_new_holding.setText("Browse holdings:")

        # Label_Credits
        self.label_label_credits_browse_holding.move(width_unit*81, height_unit*80)
        self.label_label_credits_browse_holding.setText('Credits:')
        self.label_credits_browse_holding.move(width_unit*84, height_unit*80)

        # TextBox_Browse_New_Holding
        self.textbox_browse_new_holding.move(width_unit*82, height_unit*5)
        self.textbox_browse_new_holding.setToolTip("Browse new holding")
        self.textbox_browse_new_holding.returnPressed.connect(self.signal_browse_new_holding)

        # Button_Buy_holding
        self.button_buy_holding.move(width_unit*80.5, height_unit*83)
        self.button_buy_holding.setText("Buy Holding")
        self.button_buy_holding.clicked.connect(self.signal_buy_holding)

        # Button_Back_To_Portfolio
        self.button_back_to_portfolio.move(width_unit*7, height_unit*4)
        self.button_back_to_portfolio.setText("Back to Portfolio")
        self.button_back_to_portfolio.clicked.connect(self.signal_change_to_portfolio)

        # Buttons_To_Change_Period
        self.button_period_max.setText("MAX")
        self.button_period_max.setGeometry(width_unit * 40, height_unit * 82, width_unit * 5, height_unit * 3)
        self.button_period_max.clicked.connect(self.signal_period_max)
        self.button_period_year.setText("YEAR")
        self.button_period_year.setGeometry(width_unit * 45, height_unit * 82, width_unit * 5, height_unit * 3)
        self.button_period_year.clicked.connect(self.signal_period_year)
        self.button_period_month.setText("MONTH")
        self.button_period_month.setGeometry(width_unit * 50, height_unit * 82, width_unit * 5, height_unit * 3)
        self.button_period_month.clicked.connect(self.signal_period_month)

        # Graph
        self.layout_hold_graph_browse_holdings.addWidget(self.graph_for_browse_holdings)
        self.widget_hold_graph_browse_holdings.setLayout(self.layout_hold_graph_browse_holdings)
        self.widget_hold_graph_browse_holdings.setGeometry(width_unit*7, height_unit*10, width_unit*86, height_unit*60)
        self.graph_for_browse_holdings.setMouseEnabled(x=False, y=False)

    def init_table(self, amount_of_holdings, holding_names):
        self.table_show_all_holdings.setRowCount(amount_of_holdings)
        self.table_show_all_holdings.setColumnCount(7)
        self.table_show_all_holdings.setFont(QFont("Arial", 15))
        self.table_show_all_holdings.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set Horizontal Headers
        self.table_show_all_holdings.setHorizontalHeaderItem(0, QTableWidgetItem("Total value"))
        self.table_show_all_holdings.setHorizontalHeaderItem(1, QTableWidgetItem("Ratio %"))
        self.table_show_all_holdings.setHorizontalHeaderItem(2, QTableWidgetItem("Current price"))
        self.table_show_all_holdings.setHorizontalHeaderItem(3, QTableWidgetItem("BuyIn price"))
        self.table_show_all_holdings.setHorizontalHeaderItem(4, QTableWidgetItem("Amount of holdings"))
        self.table_show_all_holdings.setHorizontalHeaderItem(5, QTableWidgetItem("BuyIn date"))
        self.table_show_all_holdings.setHorizontalHeaderItem(6, QTableWidgetItem("Sell Holding"))
        self.table_show_all_holdings.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.table_show_all_holdings.horizontalHeader().setResizeMode(1, QHeaderView.ResizeToContents)
        self.table_show_all_holdings.horizontalHeader().setResizeMode(6, QHeaderView.ResizeToContents)
        self.table_show_all_holdings.horizontalHeader().setFont(QFont("Arial", 18))

        # Set Vertical Headers
        for i in range(amount_of_holdings):
            self.table_show_all_holdings.setVerticalHeaderItem(i, QTableWidgetItem(holding_names[i]))
        self.table_show_all_holdings.clicked.connect(self.signal_table_clicked)

    def clear_table(self):
        self.table_show_all_holdings.clear()

    def show_button_in_table(self, button, button_index):
        button.setText("Sell")
        button.clicked.connect(self.signal_sell_holding)
        self.table_show_all_holdings.setCellWidget(button_index, 6, button)

    def show_data_in_table(self, position1, position2, data):
        self.table_show_all_holdings.setItem(position1, position2, QTableWidgetItem(data))

    def set_background_color_for_total_value(self, position1, r, g, b):
        self.table_show_all_holdings.item(position1, 0).setBackground(QColor(r, g, b))

    def set_background_color_for_label_ratio(self, color):
        self.label_ratio_in_period.setStyleSheet(f"background-color: {color}")

    @staticmethod
    def update_graph(graph, title, prices, date_in_ticks, color):
        graph.clear()
        graph.setTitle(title=title)
        graph.plot(x=date_in_ticks, y=prices, pen=mkPen(color))

    def update_credits(self, user_credits):
        self.label_credits.setText(str(user_credits))
        self.label_credits.adjustSize()
        self.label_credits_browse_holding.setText(str(user_credits))
        self.label_credits_browse_holding.adjustSize()

    def update_ratio(self, ratio):
        self.label_ratio_in_period.setText(ratio)
        self.label_ratio_in_period.adjustSize()

    def update_start_price(self, start_price):
        start_price = str(round(start_price, 2)) + "$"
        self.label_price_start_of_period.setText(start_price)
        self.label_price_start_of_period.adjustSize()

    def update_account_value(self, account_value):
        self.label_account_value.setText(str(account_value))
        self.label_account_value.adjustSize()

    def browse_holding(self, holding_name, holding_price):
        self.label_holding_name.setText(holding_name)
        self.label_holding_name.adjustSize()
        self.label_holding_price.setText(str(holding_price)+ "$")
        self.label_holding_price.adjustSize()

    def browse_new_holding(self, holding_name, holding_price):
        self.label_holding_name.setText(holding_name)
        self.label_holding_name.adjustSize()
        self.label_holding_price.setText(str(holding_price))
        self.label_holding_price.adjustSize()
        self.button_buy_holding.setEnabled(True)

    def ask_buy_holdings(self):
        amount_of_holdings, ok_pressed = QInputDialog.getInt(self, "Buy Holdings", "Holdings to buy")
        return amount_of_holdings, ok_pressed

    def ask_sell_holdings(self):
        amount_of_holdings, ok_pressed = QInputDialog.getInt(self, "Sell Holdings", "Holdings to sell")
        return amount_of_holdings, ok_pressed

    def show_message_box(self, title, message):
        QMessageBox.information(self, title, message)

    def show_error(self, error):
        QMessageBox.critical(self, "error", error)

    def get_button_for_holding(self, holding):
        return {holding: QPushButton(self)}

    def change_card_to_portfolio(self, user_credits):
        self.stack.setCurrentIndex(0)
        self.textbox_browse_holdings.clear()
        self.label_credits.setText(str(user_credits))
        self.label_credits.adjustSize()

    def change_card_to_browse_holdings(self, user_credits):
        self.stack.setCurrentIndex(1)
        self.label_credits_browse_holding.setText(str(user_credits))
        self.label_credits_browse_holding.adjustSize()

    def holding_doesnt_exist(self):
        self.label_holding_name.setText("Holding doesn't exist")
        self.label_holding_name.adjustSize()
        self.button_buy_holding.setDisabled(True)
        self.show_error("Holding doesn't exist")

    def get_sender(self):
        sender = self.sender()
        return sender


class DateAxis(AxisItem):
    def tickStrings(self, values, scale, spacing):
        strings = []
        rng = max(values) - min(values)
        string, label1, label2 = self.which_period_of_time(rng)
        for x in values:
            try:
                strings.append(time.strftime(string, time.localtime(x)))
            except ValueError:
                strings.append('')
        try:
            label = time.strftime(label1, time.localtime(min(values))) + time.strftime(label2,
                                                                                       time.localtime(max(values)))
        except ValueError:
            label = ''
        return strings

    @staticmethod
    def which_period_of_time(rng):
        if rng < 3600 * 24:
            string = '%H:%M:%S'
            label1 = '%b %d -'
            label2 = ' %b %d, %Y'
            return string, label1, label2
        elif 3600 * 24 <= rng < 3600 * 24 * 30:
            string = '%d'
            label1 = '%b - '
            label2 = '%b, %Y'
            return string, label1, label2
        elif 3600 * 24 * 30 <= rng < 3600 * 24 * 30 * 24:
            string = '%b'
            label1 = '%Y -'
            label2 = ' %Y'
            return string, label1, label2
        elif rng >= 3600 * 24 * 30 * 24:
            string = '%Y'
            label1 = ''
            label2 = ''
            return string, label1, label2
