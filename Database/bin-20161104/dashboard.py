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
activeNodeId            = [0,0,0,0,0,0,0,0,0,0]
activeNodeLocation      = [0,0,0,0,0,0,0,0,0,0]

currentDateTime         = [0,0,0,0,0,0,0,0,0,0]
currentTemperature      = [0,0,0,0,0,0,0,0,0,0]
currentHumidity         = [0,0,0,0,0,0,0,0,0,0]
currentPressure         = [0,0,0,0,0,0,0,0,0,0]

lastDayLowTemperature   = [0,0,0,0,0,0,0,0,0,0]
lastDayLowHumidity      = [0,0,0,0,0,0,0,0,0,0]
lastDayLowPressure      = [0,0,0,0,0,0,0,0,0,0]

lastDayHighTemperature  = [0,0,0,0,0,0,0,0,0,0]
lastDayHighHumidity     = [0,0,0,0,0,0,0,0,0,0]
lastDayHighPressure     = [0,0,0,0,0,0,0,0,0,0]

# ***** Check for command line arguments and if debug is on -d *****
if(len(sys.argv) >= 2):
    x = sys.argv[1]
    if(x == "-d"):
        debug = 1
        print("Debug Mode is On")

# ***** Open and connect to the BIOT SQL Database *****
try:
    conn = sqlite3.connect('biot.db')
    curs = conn.cursor()
    if(debug == 1): print("Opened connection to biot.db database")

except:
    print("Error connecting to the Database", sys.exc_info()[0])
    raise

# ***** Get a list of the Active Nodes and their Locations  *****
try:
    if(debug == 1): print("\nScanning through Node Table Looking for Active Nodes")
    nodeCount = 0
    cursor = conn.execute("SELECT Node_ID, Node_Location FROM Node WHERE Node_Status = ('Active') ORDER by Node_Location asc");
    for row in cursor:
        activeNodeId[nodeCount] = row[0]
        activeNodeLocation[nodeCount] = row[1]
        if(debug == 1): print("Node ID: ",activeNodeId[nodeCount],"   Location:", activeNodeLocation[nodeCount],
                              "nodeCount: ", nodeCount)
        nodeCount += 1
    if(debug == 1): print("Total Active Nodes: ", nodeCount)

except:
    print("Error reading the Node Table for Active Nodes")
    raise

# ***** Get Most Recent Sensor Readings and the time they came in *****
n = 0
while n < nodeCount:
    if(debug == 1): print("Looking for current sensor data for Node: ", activeNodeId[n], "nodeCount: ", n)

    cursor = conn.execute('''SELECT MAX(Date_Time), Temperature, Humidity, Pressure FROM Sensor_Data
    WHERE Node_ID = ?''', (activeNodeId[n],));

    for row in cursor:
        currentDateTime[n] = row[0]
        currentTemperature[n] = row[1]
        currentHumidity[n] = row[2]
        currentPressure[n] = row[3]
        if(debug==1):print("Current Date_Time = ", currentDateTime[n],
                           " Temperature = ", currentTemperature[n],
                           " Humidity = ", currentHumidity[n],
                           " Pressure = ", currentPressure[n])
    n += 1

# ***** Get the last 24 hour High/Low readings *****
nowTime = int(time.time())
aDayAgo = nowTime-(24*60*60)

n = 0
while n < nodeCount:
    if(debug == 1): print("Looking for most High/Low Range for Node: ", activeNodeId[n], "nodeCount: ", n)
    # Get the High Temperature
    cursor = conn.execute('''SELECT MAX(Temperature) FROM Sensor_Data WHERE Node_ID = ? AND Date_Time > ?''',
                          (activeNodeId[n], aDayAgo));
    for row in cursor:
        lastDayHighTemperature[n] = row[0]
        if(debug == 1): print("Max Temperature = ", lastDayHighTemperature[n])

    # Get the Low Temperature
    cursor = conn.execute('''SELECT MIN(Temperature) FROM Sensor_Data WHERE Node_ID = ? AND Date_Time > ?''',
                          (activeNodeId[n], aDayAgo));
    for row in cursor:
        lastDayLowTemperature[n] = row[0]
        if(debug == 1): print("Min Temperature = ", lastDayLowTemperature[n])

    # Get the High Humidity
    cursor = conn.execute('''SELECT MAX(Humidity) FROM Sensor_Data WHERE Node_ID = ? AND Date_Time > ?''',
                          (activeNodeId[n], aDayAgo));
    for row in cursor:
        lastDayHighHumidity[n] = row[0]
        if(debug == 1): print("Max Humidity = ", lastDayHighHumidity[n])

    # Get the Low Humidity
    cursor = conn.execute('''SELECT MIN(Humidity) FROM Sensor_Data WHERE Node_ID = ? AND Date_Time > ?''',
                          (activeNodeId[n], aDayAgo));
    for row in cursor:
        lastDayLowHumidity[n] = row[0]
        if(debug == 1): print("Min Humidity = ", lastDayHighHumidity[n])

    # Get the High Pressure
    cursor = conn.execute('''SELECT MAX(Pressure) FROM Sensor_Data WHERE Node_ID = ? AND Date_Time > ?''',
                          (activeNodeId[n], aDayAgo));
    for row in cursor:
        lastDayHighPressure[n] = row[0]
        if(debug == 1): print("Max Pressure = ", lastDayHighPressure[n])

    # Get the Low Pressure
    cursor = conn.execute('''SELECT MIN(Pressure) FROM Sensor_Data WHERE Node_ID = ? AND Date_Time > ?''',
                          (activeNodeId[n], aDayAgo));
    for row in cursor:
        lastDayLowPressure[n] = row[0]
        if(debug == 1): print("Min Pressure = ", lastDayHighPressure[n])
    n += 1    
if(debug == 1): print("\nnodeCount: ", nodeCount)
# ***** Print the Dashboard *****
print("Location         Temp.  24 hr Range   Hum.   24 hr Range   Pressure   24 hr Range")
print("-------------    -----  -----------   -----  -----------   --------  -------------")
n = 0
while n < nodeCount:
    print(activeNodeLocation[n], "\t", currentTemperature[n], " ", lastDayHighTemperature[n], "/", lastDayLowTemperature[n],
          " ", currentHumidity[n], " ", lastDayHighHumidity[n], "/", lastDayLowHumidity[n],
          " ",currentPressure[n], "   ", lastDayHighPressure[n], "/", lastDayLowPressure[n])
    n += 1

