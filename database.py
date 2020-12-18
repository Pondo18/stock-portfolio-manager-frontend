import requests


def get_username_by_hashcode(hashcode):
    payload = {'hashcode': hashcode}
    r = requests.get("http://127.0.0.1:5000/users", params=payload)
    username = r.json()[0]["username"]
    return username


def get_credits_by_username(username):
    r = requests.get(f"http://127.0.0.1:5000/users/{username}")
    user_credits = r.json()["credits"]
    return user_credits


def get_holdings_from_user(username):
    r = requests.get(f"http://127.0.0.1:5000/users/{username}/holdings")
    holdings = r.json()
    return holdings


def create_new_user(hashcode, username):
    entry_data = {'hashcode': hashcode, 'username': username}
    r = requests.post("http://127.0.0.1:5000/users", json=entry_data)
    return r.json()


def username_already_exists(username):
    r = requests.get(f"http://127.0.0.1:5000/users/{username}")
    return r.status_code == 200


def create_new_holding(username, holding, number, buy_in):
    entry_data = {'holding': holding, 'number': number, 'buyIn': buy_in}
    r = requests.post(f"http://127.0.0.1:5000/users/{username}/holdings", json=entry_data)
    return r.json()


def change_number_of_holdings(username, holding, number, buy_in):
    entry_data = {'number': number, 'buyIn': buy_in}
    r = requests.put(f"http://127.0.0.1:5000/users/{username}/holdings/{holding}", json=entry_data)
    return r.json()


def change_credits(username, new_credits):
    entry_data = {'credits': new_credits}
    r = requests.put(f"http://127.0.0.1:5000/users/{username}", json=entry_data)
    return r.json()


def get_amount_of_holdings_user_already_has(username, holding):
    r = requests.get(f"http://127.0.0.1:5000/users/{username}/holdings/{holding}")
    try:
        number = r.json()["number"]
        return number
    except TypeError:
        return 0


def user_already_has_holding(username, holding):
    r = requests.get(f"http://127.0.0.1:5000/users/{username}/holdings/{holding}")
    try:
        holding = r.json()["holding"]
        return True
    except TypeError:
        return False


def get_buy_in_price(username, holding):
    r = requests.get(f"http://127.0.0.1:5000/users/{username}/holdings/{holding}")
    buy_in = r.json()["buyIn"]
    return buy_in


def get_holding_names_from_user(username):
    r = requests.get(f"http://127.0.0.1:5000/users/{username}/holdings")
    holdings = r.json()
    holding_names = []
    for holding in holdings:
        holding_names.append(holding["holding"])
    return holding_names
