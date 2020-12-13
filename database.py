import requests


def get_username_by_hashcode(hashcode):
    payload = {'hashcode': hashcode}
    r = requests.get("http://127.0.0.1:5000/users", params=payload)
    return r.json()[0]["username"]


def synchro(username):
    r = requests.get(f"http://127.0.0.1:5000/users/{username}")
    print(r.json())
    return r.json()["hashcode"], r.json()["credits"]


def get_holdings_from_user(username):
    r = requests.get(f"http://127.0.0.1:5000/users/{username}/holdings")
    return r.json()

# TODO: funktioniert noch nicht
def create_entry(hashcode, username):
    entry_data = {'hashcode': hashcode, 'username': username}
    r = requests.post("http://127.0.0.1:5000/users", json=entry_data)
    return r.text


print(create_entry("03a147434c16b49e16304cd4faaf832d", "MoritzXY"))
#print(get_username_by_hashcode("03a147434c16b49e16304cd4faaf832d"))
#print(synchro("MoritzABC"))
