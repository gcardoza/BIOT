#!/usr/bin/python3

# Project:	BIOT Home IOT Base Station - Sensor Data Dashboard
# Author:	Geofrey Cardoza
# Company:	Excaliber Inc. (c)
# Baseline:	September 14th, 2016
# Revision:	September 14th, 2016  v0.1
#

import serial
import sys
import sqlite3
import time
import paho.mqtt.client as mqtt


# =============================================  Main Program ================================================= 
debug = 0

# The variables below are indexed by the active node count (not Node_ID) 0 = first, 1 = second etc.
activeNodeId            = []
activeNodeLocation      = []

currentDateTime         = []
currentTemperature      = []
currentHumidity         = []
currentPressure         = []

lastDayLowTemperature   = []
lastDayLowHumidity      = []
lastDayLowPressure      = []

lastDayHighTemperature  = []
lastDayHighHumidity     = []
lastDayHighPressure     = []

# ***** Check for command line arguments and if debug is on -d *****
if (len(sys.argv) >= 2):
    x = sys.argv[1]
    if (x == "-d"):
        debug = 1
        print("Debug Mode is On")

# ***** Open and connect to the BIOT SQL Database *****
try:
    conn = sqlite3.connect('biot.db')
    curs = conn.cursor()
    if (debug == 1): print("Opened connection to biot.db database")

except:
    print("Error connecting to the Database", sys.exc_info()[0])
    raise

# ***** Get a list of the Active Nodes and their Locations  *****
try:
    if (debug == 1): print("\nScanning through Node Table Looking for Active Nodes")
    nodeCount = 0
    cursor = conn.execute("SELECT Node_ID, Node_Location FROM Node WHERE Node_Status = ('Active')");
    for row in cursor:
        activeNodeId.append(row[0])
        activeNodeLocation.append(row[1])
        if(debug == 1): print("Node ID: ",activeNodeId[nodeCount],"   Location:", activeNodeLocation[nodeCount], "nodeCount: ", nodeCount)
        nodeCount += 1
    if(debug == 1): print("Total Active Nodes: ", nodeCount)

except:
    print("Error reading the Node Table for Active Nodes")
    raise

# ***** Get Most Recent Sensor Readings and the time they came in *****
n = 0
while n < nodeCount:
    if (debug == 1): print("Looking for most recent sensor data for Node: ", activeNodeId[n], "nodeCount: ", n)

    cursor = conn.execute('''SELECT Date_Time, Temperature, Humidity, Pressure FROM Sensor_Data
    WHERE Node_ID = ? AND Date_Time = (SELECT MAX(DATE_TIME) FROM Sensor_Data)''', (activeNodeId[n],));

    for row in cursor:
        currentDateTime.append(row[0])
        currentTemperature.append(row[1])
        currentHumidity.append(row[2])
        currentPressure.append(row[3])
    n += 1

# ***** Get the last 24 hour High/Low readings *****
nowTime = int(time.time())
twentyFoursAgo = nowTime-(24*60*60)

n = 0
while n < nodeCount:
    if (debug == 1): print("Looking for most High/Low Range for Node: ", activeNodeId[n], "nodeCount: ", n)
    # Get the High Temperature
    cursor = conn.execute('''SELECT MAX(Temperature) FROM Sensor_Data WHERE Node_ID = ? AND Date_Time > ?''',
                          (activeNodeId[n], twentyFoursAgo));
    for row in cursor: lastDayHighTemperature.append(row[0])

    # Get the Low Temperature
    cursor = conn.execute('''SELECT MIN(Temperature) FROM Sensor_Data WHERE Node_ID = ? AND Date_Time > ?''',
                          (activeNodeId[n], twentyFoursAgo));
    for row in cursor: lastDayLowTemperature.append(row[0])

    # Get the High Humidity
    cursor = conn.execute('''SELECT MAX(Humidity) FROM Sensor_Data WHERE Node_ID = ? AND Date_Time > ?''',
                          (activeNodeId[n], twentyFoursAgo));
    for row in cursor: lastDayHighHumidity.append(row[0])

    # Get the Low Humidity
    cursor = conn.execute('''SELECT MIN(Humidity) FROM Sensor_Data WHERE Node_ID = ? AND Date_Time > ?''',
                          (activeNodeId[n], twentyFoursAgo));
    for row in cursor: lastDayLowHumidity.append(row[0])

    # Get the High Pressure
    cursor = conn.execute('''SELECT MAX(Pressure) FROM Sensor_Data WHERE Node_ID = ? AND Date_Time > ?''',
                          (activeNodeId[n], twentyFoursAgo));
    for row in cursor: lastDayHighPressure.append(row[0])

    # Get the Low Pressure
    cursor = conn.execute('''SELECT MIN(Pressure) FROM Sensor_Data WHERE Node_ID = ? AND Date_Time > ?''',
                          (activeNodeId[n], twentyFoursAgo));
    for row in cursor: lastDayLowPressure.append(row[0])
    n += 1    

# ***** Print the Dashboard *****
print("\nnodeCount: ", nodeCount)

print("\nReport #2")
print("Location\tTemperature   24 hr Range\tHumidity    24 hr Range\t    Pressure\t24 hr Range")
print("--------\t-----------   -----------\t--------    -----------\t   ---------\t-----------")
n = 0
while n < nodeCount:
    print(activeNodeLocation[n], "\t", currentTemperature[n], "\t      ", lastDayHighTemperature[n], "/", lastDayLowTemperature[n],
          "\t", currentHumidity[n], "\t    ", lastDayHighHumidity[n], "/", lastDayLowHumidity[n],
          "  ",currentPressure[n], "\t", lastDayHighPressure[n], "/", lastDayLowPressure[n])
    n += 1

