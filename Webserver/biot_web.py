#!/usr/bin/python3

# Project:	BIOT Home IOT Base Station - Web Access
# Author:	Geofrey Cardoza
# Company:	Excaliber Inc. (c)
# Baseline:	June 28th, 2016
# Revision:	September 13th, 2016  v1.1
#

from flask import Flask, send_from_directory, request, jsonify
import sqlite3
import sys, getopt

# Create the Webserver application
# By default, Flask will serve static files from the 'static' folder
# Place any static files you want in that directory
app = Flask(__name__)

# ***** Connect to the biot Database *****
db_name = '../Database/biot.db'
conn = sqlite3.connect(db_name)

# ***** Define the Static Content Path
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
    c.execute('SELECT Node_Location, Node_Id, Node_Type, MAC_ADDRESS, SW_Version, Node_Status from Node ORDER by Node_Location')
    resp = []
    for row in c.fetchall():
        resp.append({
            'Node_Location': row[0],
            'Node_Id': row[1],
            'Node_type': row[2],
            'MAC_ADDRESS': row[3],
            'SW_Version': row[4],
            'Node_Status': row[5],

        })
    return jsonify(data=resp) 

@app.route('/sensordata', methods=['GET'])
def get_sensor_data():
    c = conn.cursor()
    c.execute('SELECT * FROM Sensor_Data LIMIT 10')
    resp = []
    for row in c.fetchall():
        resp.append({
            'Node_Id': row[0],
            'Data_Time': row[1],
            'Temperature': row[2],
            'Humidity': row[3],
            'Pressure': row[4],
            'Sequence': row[5],
        })

    return jsonify(data=resp) 


# Start the server
# By listening on 0.0.0.0, you listen all of your interfaces
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337)
