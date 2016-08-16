#!/usr/bin/python
#
# How to use:
# python server.py [db_file_path]

from flask import Flask, send_from_directory, request, jsonify
import sqlite3
import sys, getopt

# Create the Webserver application
# By default, Flask will serve static files from the 'static' folder
# Place any static files you want in that directory
app = Flask(__name__)

# Database connection
db_name = 'BIOT_Base.db'
if len(sys.argv) >= 2:
    db_name = sys.argv[1]
conn = sqlite3.connect('BIOT_Base.db')

# This creates an HTTP route on the server
# If you navigate to a /static/<file_name> path, it serves that file
@app.route('/static/<path>')
def static_assets(path):
    return send_from_directory('static', path)

# HTTP-API Routes
# These routes execute a query on the database and return the data
# as JSON

@app.route('/nodes', methods=['GET'])
def get_nodes():
    c = conn.cursor()    
    c.execute('SELECT * from Node')
    resp = []
    for row in c.fetchall():
        resp.append({
            'Node_Id': row[0],
            'Node_type': row[1],
            'SW_Version': row[2],
            'MAC_ADDRESS': row[3],
            'Serial_Port': row[4],
            'Node_Location': row[5],
            'Node_Status': row[6],
        })

    return jsonify(resp) 

@app.route('/sensordata', methods=['GET'])
def get_sensor_data():
    c = conn.cursor()
    c.execute('SELECT * FROM Sensor_Data')
    resp = []

    for row in c.fetchall():
        resp.append({
            'Node_Id': row[0],
            'Data_Stamp': row[1],
            'Time_Stamp': row[2],
            'DHT22_Temperature': row[3],
            'DHT22_Humidity': row[4],
            'BMP180_Temperature': row[5],
            'BMP180_Pressure': row[6],
            'Moisture_1': row[7],
            'Moisture_2': row[8],
            'Moisture_3': row[9],
            'Sequence': row[10],
        })

    return jsonify(resp) 


# Start the server
# By listening on 0.0.0.0, you listen all of your interfaces
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337)
