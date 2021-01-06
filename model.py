import os

import requests
import yaml


class Model:
    def __init__(self):

        # export ENVIRON=production/development in Commando Zeile
        environment = os.environ.get('ENVIRON', 'development')
        with open("config.yaml", "r") as yamlfile:
            self.cfg = yaml.load(yamlfile, Loader=yaml.FullLoader)

        self.api_host = self.cfg[environment]['api_endpoint']

    def get_username_by_hashcode(self, hashcode):
        payload = {'hashcode': hashcode}
        r = requests.get(f"{self.api_host}/users", params=payload)
        username = r.json()[0]["username"]
        return username

    def get_credits_by_username(self, username):
        r = requests.get(f"{self.api_host}/users/{username}")
        user_credits = r.json()["credits"]
        return user_credits

    def get_holdings_from_user(self, username):
        r = requests.get(f"{self.api_host}/users/{username}/holdings")
        if r.status_code == 204:
            return []
        holdings = r.json()
        return holdings

    def create_new_user(self, hashcode, username):
        entry_data = {'hashcode': hashcode, 'username': username}
        r = requests.post(f"{self.api_host}/users", json=entry_data)
        return r.json()

    def username_already_exists(self, username):
        r = requests.get(f"{self.api_host}/users/{username}")
        return r.status_code == 200

    def create_new_holding(self, username, holding, number, buy_in):
        entry_data = {'holding': holding, 'number': number, 'buyIn': buy_in}
        r = requests.post(f"{self.api_host}/users/{username}/holdings", json=entry_data)
        return r.json()

    def update_number_of_holdings(self, username, holding, number, buy_in):
        entry_data = {'number': number, 'buyIn': buy_in}
        r = requests.put(f"{self.api_host}/users/{username}/holdings/{holding}", json=entry_data)
        return r.json()

    def update_credits_in_database(self, username, new_credits):
        entry_data = {'credits': new_credits}
        r = requests.put(f"{self.api_host}/users/{username}", json=entry_data)
        return r.json()

    def get_amount_of_holdings_user_already_has(self, username, holding):
        r = requests.get(f"{self.api_host}/users/{username}/holdings/{holding}")
        try:
            number = r.json()["number"]
            return number
        except KeyError:
            return 0

    def user_already_has_holding(self, username, holding):
        r = requests.get(f"{self.api_host}/users/{username}/holdings/{holding}")
        try:
            holding = r.json()["holding"]
            return True
        except KeyError:
            return False

    def get_buy_in_price(self, username, holding):
        r = requests.get(f"{self.api_host}/users/{username}/holdings/{holding}")
        buy_in = r.json()["buyIn"]
        return buy_in

    def get_holding_names_from_user(self, username):
        r = requests.get(f"{self.api_host}/users/{username}/holdings")
        if r.status_code == 204:
            return []
        holdings = r.json()
        holding_names = []
        for holding in holdings:
            holding_names.append(holding["holding"])
        return holding_names

    def user_has_no_holdings(self, username):
        r = requests.get(f"{self.api_host}/users/{username}/holdings")
        status_code = r.status_code
        return status_code == 204

    def remove_holding(self, username, holding):
        r = requests.delete(f"{self.api_host}/users/{username}/holdings/{holding}")
        return r.json()

    def test(self):
        entry_data = {'username': "username"}
        r = requests.post(f"{self.api_host}/users", json=entry_data)
        return r.json()
