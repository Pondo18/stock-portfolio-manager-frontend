import requests


def get_username_by_hashcode(hashcode):
    payload = {'hashcode': hashcode}
    r = requests.get("http://127.0.0.1:5000/users", params=payload)
    return r.json()[0]["username"]


def get_credits_by_username(username):
    r = requests.get(f"http://127.0.0.1:5000/users/{username}")
    return r.json()["credits"]


def get_holdings_from_user(username):
    r = requests.get(f"http://127.0.0.1:5000/users/{username}/holdings")
    return r.json()


def create_entry(hashcode, username):
    entry_data = {'hashcode': hashcode, 'username': username}
    r = requests.post("http://127.0.0.1:5000/users", json=entry_data)
    return r.json()


def username_already_exists(username):
    r = requests.get(f"http://127.0.0.1:5000/users/{username}")
    return r.status_code == 200






