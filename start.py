#  import yfinance as yf
import hashlib
from pathlib import Path
import database
import register


# https://pypi.org/project/yfinance/


def login(username, password):
    hashcode = create_hash(username + ":" + password)
    print(hashcode)
    database.create_entry(hashcode, username)


def create_hash(password):
    token_file = open("token.txt", "w")
    hashcode = hashlib.md5(password.encode("utf-8")).hexdigest()
    token_file.write(hashcode)
    token_file.close()
    return hashcode


def start():
    fname = Path("/Users/moritz.moser/Documents/HDBW/1.Semester/Python/Aktien/token.txt")
    if (not fname.exists()):
        login()
    else:
        database.synchro()


def navigate(menu_items):
    count = 1
    for x in menu_items:
        print(str(count)+". "+x)
        count += 1
    which_menu = input("Navigiere durch Eingabe der In durch das Menü!\n")
    return which_menu

#def aktien_anzeigen(username):


def menu():
    menu_items = ["Portfolio", "Suche", "Watchlist"]
    navigate(menu_items)


if __name__ == "__main__":
    login()