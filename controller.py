import sys

from PyQt5.QtWidgets import QApplication

import hashcode_utils
import holdings_data_utils
from view import Register, MainGui
from model import Model


class Controller:
    def __init__(self):
        self.hashcode = ''
        self.username = ''
        self.user_credits = ''
        self.buttons_as_dict = {}
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
        self.hashcode = generated_hash
        self._model.create_new_user(generated_hash, entered_username)

    # Main_Gui Window
    def init_main_gui_widgets(self):
        user_credits = self._model.get_credits_by_username(self.username)
        self._main_gui.init_portfolio( self.size_units, user_credits)
        self._main_gui.init_browse_holdings(self.size_units)
        first_holding = self.get_first_holding_from_user()
        self.init_graph(first_holding)
        self.table_first_init()

    def table_first_init(self):
        self.init_table()
        self.show_holdings_in_table()

    def init_table(self):
        holding_names = self._model.get_holding_names_from_user(self.username)
        amount_of_holdings = len(holding_names)
        self._main_gui.init_table(amount_of_holdings, holding_names)

    def update_table(self):
        user_credits = self._model.get_credits_by_username(self.username)
        self._main_gui.update_credits(user_credits)
        self._main_gui.update_table()
        self.init_table()
        self.show_holdings_in_table()

    def clicked_table(self, item):
        holding_names = self._model.get_holding_names_from_user(self.username)
        row = item.row()
        clicked_holding_row = holding_names[row]
        self.update_graph(clicked_holding_row, "1y", self._main_gui.graph_for_portfolio)

    def show_holdings_in_table(self):
        holdings = self._model.get_holdings_from_user(self.username)
        holdings_data = self.get_holdings_data_for_portfolio(holdings)
        amount_of_holdings = len(holdings)

        positions = [(i, j) for i in range(amount_of_holdings) for j in range(4)]
        for position, data in zip(positions, holdings_data):
            if data == '':
                continue
            self._main_gui.show_data_in_table(position[0], position[1], data)
        self.show_buttons_in_table()

    def show_buttons_in_table(self):
        holdings = self._model.get_holding_names_from_user(self.username)
        buttons_as_dict = self.buttons_to_dict()
        button_index = 0
        for holding in holdings:
            button = buttons_as_dict[holding]
            self._main_gui.show_button_in_table(button, button_index)
            button_index += 1

    def init_graph(self, first_holding):
        self.update_graph(first_holding, "1Y", self._main_gui.graph_for_portfolio)

    def update_graph(self, holding, period, graph):
        holding_data = holdings_data_utils.get_holding_price_for_period(holding, period)
        prices = holding_data.values
        date = holding_data.keys()
        date_in_ticks = self.date_in_ticks(date)
        self._main_gui.update_graph(graph, holding, prices, date_in_ticks)

    def buy_holding(self):
        number_to_buy, is_buy_holding = self.how_many_holdings("buy")
        if is_buy_holding:
            holding = self._main_gui.label_holding_name.text()
            holding_price = float(self._main_gui.label_holding_price.text())
            holding_price = int(round(holding_price))
            user_credits = self._model.get_credits_by_username(self.username)
            if self._model.user_already_has_holding(self.username, holding):
                number_of_holdings_user_already_has = self._model.get_amount_of_holdings_user_already_has(self.username,
                                                                                                          holding)
                if user_credits > holding_price * number_to_buy:
                    old_buy_in_price = self._model.get_buy_in_price(self.username, holding)
                    number_of_total_holdings = number_of_holdings_user_already_has + number_to_buy
                    new_buy_in_price = (old_buy_in_price * number_of_holdings_user_already_has
                                        + holding_price * number_to_buy) / number_of_total_holdings
                    new_buy_in_price = round(new_buy_in_price, 2)
                    self._model.update_number_of_holdings(self.username, holding, number_of_total_holdings,
                                                          new_buy_in_price)
                    new_amount_of_credits = user_credits - holding_price * number_to_buy
                    self._model.update_credits_in_database(self.username, new_amount_of_credits)
                    self._main_gui.update_credits(new_amount_of_credits)
                    self._main_gui.show_message_box("Buy", "Bought holding!")
                else:
                    self._main_gui.show_error('Not enough credits')
            else:
                if user_credits > holding_price * number_to_buy:
                    self._model.create_new_holding(self.username, holding, number_to_buy, holding_price)
                    new_amount_of_credits = user_credits - holding_price * number_to_buy
                    self._model.update_credits_in_database(self.username, new_amount_of_credits)
                    self._main_gui.show_message_box("Buy", "Bought new holding!")
                else:
                    self._main_gui.show_error('Not enough credits')

    def sell_holding(self):
        number_to_sell, is_sell_holding = self.how_many_holdings("sell")
        if is_sell_holding:
            holding = self.get_holding_of_sender()
            old_user_credits = self._model.get_credits_by_username(self.username)
            old_amount_of_holdings = self._model.get_amount_of_holdings_user_already_has(self.username, holding)
            current_holding_price = holdings_data_utils.get_current_price_of_holding(holding)
            new_amount_of_credits = old_user_credits + current_holding_price * number_to_sell
            new_amount_of_holdings = old_amount_of_holdings - number_to_sell
            buy_in = self._model.get_buy_in_price(self.username, holding)

            self._model.update_credits_in_database(self.username, new_amount_of_credits)
            self._model.update_number_of_holdings(self.username, holding, new_amount_of_holdings, buy_in)
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
            self.update_graph(holding_name, "1y", self._main_gui.graph_for_browse_holdings)
        else:
            self._main_gui.holding_doesnt_exist()

    def change_card_to_browse_holdings(self):
        holding_name = self._main_gui.textbox_browse_holdings.text()
        if self.browse_holding(holding_name):
            self.update_graph(holding_name, "1y", self._main_gui.graph_for_browse_holdings)
        user_credits = self._model.get_credits_by_username(self.username)
        self._main_gui.change_card_to_browse_holdings(user_credits)

    def change_card_to_portfolio(self):
        user_credits = self._model.get_credits_by_username(self.username)
        self._main_gui.change_card_to_portfolio(user_credits)
        self.update_table()

    def how_many_holdings(self, action):
        if action == "buy":
            amount_of_holdings, ok_pressed = self._main_gui.ask_buy_holdings()
        if action == "sell":
            amount_of_holdings, ok_pressed = self._main_gui.ask_sell_holdings()
        if ok_pressed:
            if amount_of_holdings == 0:
                return 0, ok_pressed
            return amount_of_holdings, ok_pressed
        else:
            return 0, ok_pressed

    def get_first_holding_from_user(self):
        if not self._model.user_has_no_holdings(self.username):
            first_holding = self._model.get_holding_names_from_user(self.username)[0]
            return first_holding
        else:
            return "aapl"

    def buttons_to_dict(self):
        holdings = self._model.get_holding_names_from_user(self.username)
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

    def get_holding_of_sender(self):
        sender = self._main_gui.get_sender()
        holding = list(self.buttons_as_dict.keys())[list(self.buttons_as_dict.values()).index(sender)]
        return holding

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

    @staticmethod
    def date_in_ticks(dates):
        return [date.timestamp() for date in dates]

    def run_start(self):
        if hashcode_utils.return_hash_if_exists()[1]:
            self.username = self.get_username()
            self._main_gui.show()
            self.init_main_gui_widgets()
        else:
            self._register.show()
        return self._app.exec_()

    def run_main_gui(self):
        self.init_main_gui_widgets()
        self._register.close()
        self._main_gui.show()


if __name__ == "__main__":
    controller = Controller()
    sys.exit(controller.run_start())
