from functools import wraps
import psycopg2
from flask import Flask, request, jsonify, session
from db_config import connect_db
from schema import create_table
from _datetime import datetime, timedelta, timezone
import jwt
from flask_session import Session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pavan0011'

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'session:'
Session(app)

# Token Middleware
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(user_id, *args, **kwargs)
    return decorated

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


@app.route('/user/<int:id_no>', methods=['GET'])
def get_user(id_no):
    connection = connect_db()
    cursor = connection.cursor()
    try:

        cursor.execute("""select id_no, name, email from users where id_no = %s""", (id_no,))
        result = cursor.fetchone()

        if result:
            user = {"id_no": result[0], "name": result[1], "email": result[2]}
            return jsonify(user)
        else:
            return {"message": "User not found"}
    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        cursor.close()
        connection.close()


@app.route('/update/<int:id_no>', methods=['PUT'])
def update_user(id_no):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        number = data.get('number')

        cursor.execute("""update users set name = %s, email = %s, number = %s where id_no = %s""", (name, email, number, id_no))
        connection.commit()
        return {"message": "User Updated"}

    except Exception as e:
        return jsonify({"error": str(e)})

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
    cursor = connection.cursor()
    try:
        cursor.execute("""
        select id_no, password from users
        where name = %s""", (name,))
        result = cursor.fetchone()

        if result:
            userid, stored_password = result
            if stored_password == password:
                playload = {
                    'user_id': userid,
                    'exp': datetime.now(timezone.utc) + timedelta(minutes=30)
                }
                token = jwt.encode(playload, app.config['SECRET_KEY'], algorithm='HS256')

                cursor.execute("UPDATE users SET tokens = %s WHERE id_no = %s", (token, userid))
                connection.commit()
                return {"message": "User Logged In!"}

            else:
                return {"message": "Wrong Password"}
        else:
            return {"message": "User not found"}

    except psycopg2.Error as e:
        error_msg = str(e)
        print('Database error:', error_msg)
        return {"error": error_msg}

    finally:
        cursor.close()
        connection.close()

@app.route('/logout/<int:id_no>', methods=['POST'])
def logout_user(id_no):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""select * from users where id_no = %s""", (id_no,))
        result = cursor.fetchone()

        if result:
            userid = result[0]

            cursor.execute("""update users set tokens = NULL where id_no = %s""", (id_no,))
            connection.commit()
            return {"message": "User Logged Out!"}

        else:
            return {"Error": "Invalid Token"}

    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    create_table()
    app.run(debug=True)