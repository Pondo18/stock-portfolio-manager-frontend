import requests

def get_hash():
    token_file = open("token.txt", "r")
    return token_file.read().rstrip()


def get_username_by_hashcode(hashcode):
    payload = {'hashcode': hashcode}
    r = requests.get("http://127.0.0.1:5000/users", params=payload)

    return r.json()["username"]


def synchro(username):
    r = requests.get(f"http://127.0.0.1:5000/users/{username}")
    return r.json()["hashcode"], r.json()["credits"]





def create_entry(hashcode, username):
    entry_data = {'hashcode': hashcode, 'username': username, 'credits': '0'}
    r = requests.post("http://127.0.0.1:5000/users", data=entry_data)
    return r.text


#print(create_entry("03a147434c16b49e16304cd4faaf832d", "MoritzXY"))
print(synchro("MoritzXYZ"))

"""
import mysql.connector


mydb = mysql.connector.connect(
    host="localhost",
    user="moritz",
    password="secret",
    database="finance"
)


def get_hash():
    token_file = open("token.txt", "r")
    return token_file.read().rstrip()


def synchro():
    mycursor = mydb.cursor()
    sqlStatement = "Select username, credits from userdata where hashcode = %s"
    val = (get_hash(),)
    mycursor.execute(sqlStatement, val)
    myresult = mycursor.fetchall()
    mycursor.close()
    return myresult


def create_entry(hashcode, username):
    mycursor = mydb.cursor()
    sqlStatement = "insert into userdata (hashcode, username, credits) values (%s, %s, %s)"
    val = (hashcode, username, 0)
    mycursor.execute(sqlStatement, val)
    mydb.commit()
    mycursor.close()
"""