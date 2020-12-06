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
