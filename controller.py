import re
import sys

from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QApplication

from enum import Enum

import operator

import hashcode_utils
import holdings_data_utils
from view import Register, MainGui
from model import Model


class Controller:
    def __init__(self):
        self.username = ''
        self.buttons_as_dict = {}
        self.holding_names = []
        self._app = QApplication(sys.argv)
        self._model = Model()
        self.screen = self._app.primaryScreen()
        self.size = self.screen.size()
        self.size_units = {"width_unit": round(self.size.width() / 100), "height_unit": round(self.size.height() / 100)}
        self._register = Register(self.size)
        self._main_gui = MainGui(self.size)
        self.init_me()

    def init_me(self):
        self._register.enter_pressed.connect(self.do_register)
        self._main_gui.signal_table_clicked.connect(self.clicked_table)
        self._main_gui.signal_buy_holding.connect(self.buy_holding)
        self._main_gui.signal_sell_holding.connect(self.sell_holding)
        self._main_gui.signal_change_to_portfolio.connect(self.change_card_to_portfolio)
        self._main_gui.signal_change_to_browse_holdings.connect(self.change_card_to_browse_holdings)
        self._main_gui.signal_browse_new_holding.connect(self.browse_new_holding)
        self._main_gui.signal_period_max.connect(self.change_period)
        self._main_gui.signal_period_year.connect(self.change_period)
        self._main_gui.signal_period_month.connect(self.change_period)

    # Register Window
    def do_register(self):
        typed_in_username = self._register.textbox_username.text()
        length_username = len(typed_in_username)
        typed_in_password = self._register.textbox_password.text()
        if not self._model.username_already_exists(typed_in_username):
            if not length_username > 20:
                self.username = typed_in_username
                self.register(typed_in_username, typed_in_password)
                self.run_main_gui()
            else:
                self._register.error("Username shouldn't be longer than 20 characters")
        else:
            self._register.error("Username already taken")

    def register(self, entered_username, password):
        credentials_concatenated = entered_username + ":" + password
        generated_hash = hashcode_utils.create_hash(credentials_concatenated)
        self._model.create_new_user(generated_hash, entered_username)

    # Main_Gui Window
    def init_main_gui_widgets(self):
        user_credits = self._model.get_credits_by_username(self.username)
        self._main_gui.init_portfolio(self.size_units, user_credits)
        self._main_gui.init_browse_holdings(self.size_units)
        self.table_first_init()
        first_holding = self.get_first_holding_from_user()
        self.init_graph(first_holding)

    def table_first_init(self):
        holdings = self._model.get_holdings_from_user(self.username)
        holdings_data, holding_names = self.get_holdings_data_for_portfolio(holdings)
        self.init_table(holding_names)
        self.show_holdings_in_table(holdings_data)

    def init_table(self, holding_names):
        amount_of_holdings = len(holding_names)
        self._main_gui.init_table(amount_of_holdings, holding_names)

    def update_table(self):
        holdings = self._model.get_holdings_from_user(self.username)
        holdings_data, holding_names = self.get_holdings_data_for_portfolio(holdings)
        user_credits = self._model.get_credits_by_username(self.username)
        self._main_gui.update_credits(user_credits)
        self._main_gui.clear_table()
        self.init_table(holding_names)
        self.show_holdings_in_table(holdings_data)

    def clicked_table(self, item):
        holding_names = self.holding_names
        row = item.row()
        clicked_holding_row = holding_names[row]
        holding_data = holdings_data_utils.get_holding_price_for_period(clicked_holding_row, "1y")
        prices = holding_data.values
        date = holding_data.keys()
        self.update_graph(clicked_holding_row, prices, date, self._main_gui.graph_for_portfolio)

    def init_graph(self, first_holding):
        holding_data = holdings_data_utils.get_holding_price_for_period(first_holding, "1y")
        prices = holding_data.values
        date = holding_data.keys()
        self.update_graph(first_holding, prices, date, self._main_gui.graph_for_portfolio)

    def update_graph(self, holding, prices, dates, graph):
        date_in_ticks = self.date_in_ticks(dates)
        amount_of_saved_prices = len(prices)
        if prices[0] > prices[amount_of_saved_prices-1]:
            self._main_gui.update_graph(graph, holding, prices, date_in_ticks, 'r')
        else:
            self._main_gui.update_graph(graph, holding, prices, date_in_ticks, 'g')

    def update_ratio_in_period(self, price_start_of_period, price_end_of_period):
        ratio = self.get_ratio(price_end_of_period, price_start_of_period)
        self._main_gui.update_ratio(ratio)
        if ratio[0] == "+":
            self._main_gui.set_background_color_for_label_ratio("green")
        if ratio[0] == "-":
            self._main_gui.set_background_color_for_label_ratio("red")
        self._main_gui.update_start_price(price_start_of_period)

    def change_period(self):
        sender = self._main_gui.get_sender()
        holding = self._main_gui.label_holding_name.text()
        if sender.geometry() == QRect(680, 820, 85, 30):
            period = "max"
        if sender.geometry() == QRect(765, 820, 85, 30):
            period = "1y"
        if sender.geometry() == QRect(850, 820, 85, 30):
            period = "1mo"
        holding_data = holdings_data_utils.get_holding_price_for_period(holding, period)
        prices = holding_data.values
        date = holding_data.keys()
        self.update_graph(holding, prices, date, self._main_gui.graph_for_browse_holdings)
        self.update_ratio_in_period(prices[0], prices[-1])

    def show_holdings_in_table(self, holdings_data):
        holdings = self._model.get_holdings_from_user(self.username)
        amount_of_holdings = len(holdings)

        positions = [(i, j) for i in range(amount_of_holdings) for j in range(6)]
        for position, data in zip(positions, holdings_data):
            if data == '':
                continue
            if position[1] == 1:
                self.which_color_for_current_price(position[0], data)
            self._main_gui.show_data_in_table(position[0], position[1], data)
        self.show_buttons_in_table()

    def show_buttons_in_table(self):
        holdings = self.holding_names
        buttons_as_dict = self.buttons_to_dict()
        button_index = 0
        for holding in holdings:
            button = buttons_as_dict[holding]
            self._main_gui.show_button_in_table(button, button_index)
            button_index += 1

    def buy_holding(self):
        number_to_buy, is_buy_holding = self.how_many_holdings(HoldingAction.BUY)
        if is_buy_holding:
            holding = self._main_gui.label_holding_name.text()
            holding_price = holdings_data_utils.get_current_price_of_holding(holding)
            user_credits = self._model.get_credits_by_username(self.username)
            if self._model.user_already_has_holding(self.username, holding):
                number_of_holdings_user_already_has = self._model.get_amount_of_holdings_user_already_has(self.username,
                                                                                                          holding)
                if user_credits > holding_price * number_to_buy:
                    self.buy_old_holding_again(holding, number_of_holdings_user_already_has, number_to_buy,
                                               user_credits, holding_price)
                else:
                    self._main_gui.show_error('Not enough credits')
            else:
                if user_credits > holding_price * number_to_buy:
                    self.buy_new_holding(holding, number_to_buy, holding_price, user_credits)
                else:
                    self._main_gui.show_error('Not enough credits')

    def buy_old_holding_again(self, holding, number_of_holdings_user_already_has, number_to_buy,
                              user_credits, holding_price):
        old_buy_in_price = self._model.get_buy_in_price(self.username, holding)
        number_of_total_holdings = number_of_holdings_user_already_has + number_to_buy
        new_buy_in_price = (old_buy_in_price * number_of_holdings_user_already_has
                            + holding_price * number_to_buy) / number_of_total_holdings
        new_buy_in_price = round(new_buy_in_price, 2)
        self._model.update_number_of_holdings(self.username, holding, number_of_total_holdings,
                                              new_buy_in_price)
        new_amount_of_credits = round(user_credits - holding_price * number_to_buy)
        self._model.update_credits_in_database(self.username, new_amount_of_credits)
        self._main_gui.update_credits(new_amount_of_credits)
        self._main_gui.show_message_box("Buy", "Bought holding!")

    def buy_new_holding(self, holding, number_to_buy, holding_price, user_credits):
        self._model.create_new_holding(self.username, holding, number_to_buy, holding_price)
        new_amount_of_credits = round(user_credits - holding_price * number_to_buy)
        self._model.update_credits_in_database(self.username, new_amount_of_credits)
        self._main_gui.update_credits(new_amount_of_credits)
        self._main_gui.show_message_box("Buy", "Bought new holding!")

    def sell_holding(self):
        number_to_sell, is_sell_holding = self.how_many_holdings(HoldingAction.SELL)
        if is_sell_holding:
            holding = self.get_holding_of_sender()
            old_user_credits = self._model.get_credits_by_username(self.username)
            old_amount_of_holdings = self._model.get_amount_of_holdings_user_already_has(self.username, holding)
            if old_amount_of_holdings >= number_to_sell:
                self.do_sell_holding(holding, old_user_credits, number_to_sell, old_amount_of_holdings)
            else:
                self._main_gui.show_error("Not enough holdings")

    def do_sell_holding(self, holding, old_user_credits, number_to_sell, old_amount_of_holdings):
        current_holding_price = holdings_data_utils.get_current_price_of_holding(holding)
        new_amount_of_credits = round(old_user_credits + current_holding_price * number_to_sell)
        new_amount_of_holdings = old_amount_of_holdings - number_to_sell
        buy_in = self._model.get_buy_in_price(self.username, holding)

        self._model.update_credits_in_database(self.username, new_amount_of_credits)
        self._model.update_number_of_holdings(self.username, holding, new_amount_of_holdings, buy_in)
        if new_amount_of_holdings == 0:
            self._model.remove_holding(self.username, holding)
        self.update_table()

    def browse_holding(self, holding_name):
        if holdings_data_utils.holding_exists(holding_name):
            holding_price = holdings_data_utils.get_current_price_of_holding(holding_name)
            self._main_gui.browse_holding(holding_name, holding_price)
            return True
        else:
            self._main_gui.holding_doesnt_exist()
            return False

    def browse_new_holding(self):
        holding_name = self._main_gui.textbox_browse_new_holding.text()
        if holdings_data_utils.holding_exists(holding_name):
            holding_price = holdings_data_utils.get_current_price_of_holding(holding_name)
            self._main_gui.browse_new_holding(holding_name, holding_price)
            holding_data = holdings_data_utils.get_holding_price_for_period(holding_name, "1y")
            prices = holding_data.values
            date = holding_data.keys()
            self.update_graph(holding_name, prices, date, self._main_gui.graph_for_browse_holdings)
            self.update_ratio_in_period(prices[0], prices[-1])
        else:
            self._main_gui.holding_doesnt_exist()

    def change_card_to_browse_holdings(self):
        holding_name = self._main_gui.textbox_browse_holdings.text()
        if self.browse_holding(holding_name):
            holding_data = holdings_data_utils.get_holding_price_for_period(holding_name, "1y")
            prices = holding_data.values
            date = holding_data.keys()
            self.update_graph(holding_name, prices, date, self._main_gui.graph_for_browse_holdings)
            self.update_ratio_in_period(prices[0], prices[-1])
        user_credits = self._model.get_credits_by_username(self.username)
        self._main_gui.change_card_to_browse_holdings(user_credits)

    def change_card_to_portfolio(self):
        user_credits = self._model.get_credits_by_username(self.username)
        self._main_gui.change_card_to_portfolio(user_credits)
        self.update_table()
        first_holding = self.get_first_holding_from_user()
        holding_data = holdings_data_utils.get_holding_price_for_period(first_holding, "1y")
        prices = holding_data.values
        date = holding_data.keys()
        self.update_graph(first_holding, prices, date, self._main_gui.graph_for_portfolio)

    def how_many_holdings(self, action):
        if action == HoldingAction.BUY:
            amount_of_holdings, ok_pressed = self._main_gui.ask_buy_holdings()
        if action == HoldingAction.SELL:
            amount_of_holdings, ok_pressed = self._main_gui.ask_sell_holdings()
        if ok_pressed:
            if amount_of_holdings == 0:
                return 0, ok_pressed
            return amount_of_holdings, ok_pressed
        else:
            return 0, ok_pressed

    def get_first_holding_from_user(self):
        if len(self.holding_names) > 0:
            first_holding = self.holding_names[0]
            return first_holding
        else:
            return 'aapl'

    def buttons_to_dict(self):
        holdings = self.holding_names
        buttons_from_holdings = {}
        for holding in holdings:
            button_from_holding = self._main_gui.get_button_for_holding(holding)
            buttons_from_holdings.update(button_from_holding)
        self.buttons_as_dict = buttons_from_holdings
        return buttons_from_holdings

    def get_username(self):
        hashcode = hashcode_utils.return_hash_if_exists()[0]
        username = self._model.get_username_by_hashcode(hashcode)
        return username

    def which_color_for_current_price(self, position1, ratio):
        ratio_as_string = re.search(r"([0-9\.\-\+]+)", ratio).group()
        ratio_as_int = re.search(r"([0-9\.]+)", ratio).group()
        ratio_as_int = float(ratio_as_int)
        if ratio_as_string[0] == "+":
            r, g, b = self.which_green_color_in_rgb_for_ratio(ratio_as_int)
            self._main_gui.set_background_color_for_total_value(position1, r, g, b)
        if ratio_as_string[0] == "-":
            r, g, b = self.which_red_color_in_rgb_for_ratio(ratio_as_int)
            self._main_gui.set_background_color_for_total_value(position1, r, g, b)

    @staticmethod
    def which_green_color_in_rgb_for_ratio(ratio_int):
        if ratio_int > 10:
            return 34, 139, 34
        return 0, 238, 0

    @staticmethod
    def which_red_color_in_rgb_for_ratio(ratio_int):
        if ratio_int > 10:
            return 205, 0, 0
        return 255, 0, 0

    def get_holding_of_sender(self):
        sender = self._main_gui.get_sender()
        holding = list(self.buttons_as_dict.keys())[list(self.buttons_as_dict.values()).index(sender)]
        return holding

    def get_holdings_data_for_portfolio(self, holdings):
        data_as_two_dimensional_array = []
        total_values = []
        for holding in holdings:
            holding_data = self.get_data_for_holding(holding)
            total_values.append(holding_data[1])
            data_as_two_dimensional_array.append(holding_data)
        data_as_two_dimensional_array.sort(key=operator.itemgetter(1), reverse=True)
        total_values.sort(reverse=True)
        all_holdings_value = sum(total_values)
        user_credits = self._model.get_credits_by_username(self.username)
        account_value = round(all_holdings_value + user_credits)
        data_from_all_holdings, holding_names = self.flatten_holdings_data(data_as_two_dimensional_array, total_values)
        self.holding_names = holding_names
        self._main_gui.update_account_value(account_value)
        return data_from_all_holdings, holding_names

    @staticmethod
    def flatten_holdings_data(data_as_two_dimensional_array, total_values):
        holding_names = []
        data_from_all_holdings = []
        for i in range(len(data_as_two_dimensional_array)):
            total_value_as_string = str(total_values[i])
            data_as_two_dimensional_array[i][1] = f"{total_value_as_string}$"
            holding_names.append(data_as_two_dimensional_array[i][0])
            for j in range(1, len(data_as_two_dimensional_array[i])):
                data_from_all_holdings.append(data_as_two_dimensional_array[i][j])
        return data_from_all_holdings, holding_names

    def get_data_for_holding(self, holding):
        holding_name = holding["holding"]
        holding_price = holdings_data_utils.get_current_price_of_holding(holding_name)
        holding_price = round(holding_price, 2)
        holding_number = holding["number"]
        holding_buy_date = str(holding["buyDate"])
        total_value = holding_price * holding_number
        total_value = round(total_value, 2)
        holding_buy_in = holding["buyIn"]
        ratio = self.get_ratio(holding_price, holding_buy_in)
        holding_buy_in = str(holding_buy_in)
        holding_buy_in = holding_buy_in + "$"
        holding_price = str(holding_price) + "$"
        holding_number = str(holding_number)
        holding_data = [holding_name, total_value, ratio, holding_price,
                        holding_buy_in, holding_number, holding_buy_date]
        return holding_data

    @staticmethod
    def get_ratio(end_price, start_price):
        if end_price > start_price:
            ratio = round(end_price / start_price - 1, 4)
            ratio_as_percentage = "{:.2%}".format(ratio)
            ratio_as_percentage = "+"+ratio_as_percentage
        if end_price < start_price:
            ratio = round(abs(end_price / start_price - 1), 4)
            ratio_as_percentage = "{:.2%}".format(ratio)
            ratio_as_percentage = "-"+ratio_as_percentage
        if end_price == start_price:
            ratio_as_percentage = "0%"
        return ratio_as_percentage

    @staticmethod
    def date_in_ticks(dates):
        return [date.timestamp() for date in dates]

    def run_start(self):
        if hashcode_utils.return_hash_if_exists()[1]:
            self.username = self.get_username()
            self.init_main_gui_widgets()
            self._main_gui.show()
        else:
            self._register.show()
        return self._app.exec_()

    def run_main_gui(self):
        self.init_main_gui_widgets()
        self._register.close()
        self._main_gui.show()


class HoldingAction(Enum):
    SELL = 1
    BUY = 2


if __name__ == "__main__":
    controller = Controller()
    sys.exit(controller.run_start())
