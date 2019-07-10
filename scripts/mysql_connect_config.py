import mysql.connector


def database_connect():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",  # enter your password to your mysql database here
        database="rift_leaderboards")
    return mydb