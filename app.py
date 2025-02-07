import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_mysqldb import MySQL
import time
import MySQLdb


app = Flask(__name__)

# Configure MySQL from environment variables
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'default_user')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'default_password')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'default_db')

# Initialize MySQL
mysql = MySQL(app)


def init_db():
    retries = 5  # Number of retries
    while retries > 0:
        try:
            with app.app_context():
                cur = mysql.connection.cursor()
                try:
                    cur.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        message TEXT
                    );
                    ''')
                    mysql.connection.commit()
                    print("Database initialized successfully!")
                    return  # Exit function if successful
                finally:
                    cur.close()  # Ensure cursor is closed
        except MySQLdb.OperationalError as e:  # Catch MySQL connection errors
            print(f"Database connection failed: {e}, retrying in 5 seconds...")
            retries -= 1
            time.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return  # Exit on unexpected errors

    print("Database connection failed after multiple attempts. Exiting...")


@app.route('/')
def hello():
    cur = mysql.connection.cursor()
    cur.execute('SELECT message FROM messages')
    messages = cur.fetchall()
    cur.close()
    return render_template('index.html', messages=messages)

@app.route('/submit', methods=['POST'])
def submit():
    new_message = request.form.get('new_message')
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO messages (message) VALUES (%s)', [new_message])
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': new_message})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

