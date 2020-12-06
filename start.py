import yfinance as yf
import hashlib
from pathlib import Path
import database


# https://pypi.org/project/yfinance/


def login():
    username = input("Please enter a username:\n")  # maximal 20 zeichen
    password = input("Please enter a password:\n")  # Passwort Anforderungen hinzufügen
    hash = create_hash(username + ":" + password)
    database.create_entry(hash, username)


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


if __name__ == "__main__":
    start()
