import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'public',   # read-only user, no password
    'password': '',
    'database': 'nyc_taxi_db'
}

def fetchall(query):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result
