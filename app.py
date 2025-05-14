from flask import Flask, request

from db_config import connect_db
from schema import create_table

app = Flask(__name__)

@app.route('/register', methods = ['POST'])
def register_user():
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')
    email = data.get('email')
    number = data.get('number')

    connection = connect_db()
    if not connection:
        return {"Error": "DB Connection Failed"}

    try:
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO users (name, password, email, number)
        VALUES (%s, %s, %s, %s) """, (name, password, email, number))

        connection.commit()
        return {"message": "User Registered Successfully!"}

    except psycopg2.Error as e:
        print('error:', {e})

    finally:
        cursor.close()
        connection.close()


@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')

    if not all([name, password]):
        return {"error": "All fields are required"}

    connection = connect_db()
    if not connection:
        return {"error": "DB Connection Failed"}

    try:
        cursor = connection.cursor()
        cursor.execute("""
        select * from users
        where name = %s and password = %s""", (name, password))
        result = cursor.fetchone()

        if result:
            return {"message": "User Logged In!"}
        else:
            return {"message": "Login Failed"}

    except psycopg.Error as e:
        print('error:', {e})

    finally:
        cursor.close()
        connection.close()




if __name__ == '__main__':
    create_table()
    app.run(debug=True)