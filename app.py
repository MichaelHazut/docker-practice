from flask import Flask, request, make_response
import mysql.connector
from mysql.connector import Error
import socket
from datetime import datetime
import time
import logging


app = Flask(__name__)

logging.basicConfig(filename='/app/logs/app.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

db_config = {
    'host': 'db',
    'port': 3306,
    'database': 'counterdb',
    'user': 'root',
    'password': 'example'
}

def db_connection():
    max_attempts = 10
    delay = 5 

    for attempt in range(max_attempts):
        try:
            conn = mysql.connector.connect(**db_config)

            if conn.is_connected():
                logging.info('Connected to MySQL Server version %s', conn.get_server_info())
                return conn
        except Error as e:
            logging.error("Error connecting to MySQL: %s", e)
            logging.info("Attempt %d of %d. Retrying in %d seconds...", attempt + 1, max_attempts, delay)
            time.sleep(delay)

    raise Exception("Could not connect to MySQL server after multiple attempts")


def initialize_db():
    global counter
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS access_log (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        access_time DATETIME,
                        client_ip VARCHAR(255),
                        server_ip VARCHAR(255))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS global_counter (
                            id INT PRIMARY KEY AUTO_INCREMENT,
                            count INT DEFAULT 0)''')

    cursor.execute("SELECT COUNT(*) FROM global_counter")
    count_rows = cursor.fetchone()

    if count_rows[0] == 0:
        cursor.execute('''INSERT INTO global_counter (count) VALUES (0)''')

    conn.commit()
    cursor.close()
    conn.close()
    logging.info("Database initialized")

initialize_db()

def get_counter():
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT count FROM global_counter")
    count_rows = cursor.fetchall()

    if count_rows:
        counter = count_rows[0][0]
    else:
        counter = 0

    return counter

@app.route('/')
def index():
    counter = get_counter()
    counter += 1

    internal_ip = socket.gethostbyname(socket.gethostname())
    client_ip = request.remote_addr
    access_time = datetime.now()
    
    logging.info(f"Client IP: {client_ip}, Server IP: {internal_ip}, Access Time: {access_time}")
    
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO access_log (access_time, client_ip, server_ip) VALUES (%s, %s, %s)",
                   (access_time, client_ip, internal_ip)) 
    cursor.execute("UPDATE global_counter SET count = %s", ((counter),))
    conn.commit()
    cursor.close()
    conn.close()

    response = make_response(internal_ip)
    response.set_cookie('internal_ip', internal_ip, max_age=300) 
    return response


@app.route('/showcount')
def show_count():
    count = get_counter()
    return f"Count: {count}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
