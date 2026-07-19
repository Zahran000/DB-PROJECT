"""
student course registration system
db_connection.py — handles mysql connection
"""

import mysql.connector
from mysql.connector import Error


def get_connection():
    """
    returns a mysql connection object.
    edit host, user, password below to match your mysql setup.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",          # your mysql username
            password="system",          # your mysql password (change this)
            database="registration_db"
        )
        return connection
    except Error as e:
        print(f"[db error] could not connect to mysql: {e}")
        return None
