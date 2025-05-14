import psycopg2

DB_HOST = 'localhost'
DB_NAME = 'Employee'
DB_USER = 'postgres'
DB_PASSWORD = '0110'
DB_PORT = '8000'

def connect_db():
    connection = psycopg2.connect(
        host = DB_HOST,
        dbname = DB_NAME,
        user = DB_USER,
        password = DB_PASSWORD,
        port = DB_PORT
    )
    return connection