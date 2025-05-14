from db_config import connect_db

def create_table():
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
        id_no SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        password VARCHAR(50) NOT NULL,
        email VARCHAR(50) NOT NULL,
        number VARCHAR(10) check (number ~ '^\d{10}$')
        );
    """)

    connection.commit()
    cursor.close()
    connection.close()