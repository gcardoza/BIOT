#!/usr/bin/python3

# Project:	BIOT Base Monitoring Station - Reads data from the RIOT2+ devices
# Author:	Geofrey Cardoza
# Company:	Excaliber Inc. (c)
# Baseline:	June 28th, 2016
# Revision:	September 13th, 2016  v1.1
#

import serial
import sys
import sqlite3
import time
import datetime
import paho.mqtt.client as mqtt

debug = 0

# Check for command line arguments and if debug is on -d
if (len(sys.argv) >= 2):
    x = sys.argv[1]
    if (x == "-d"):
        debug = 1
        print("Debug Mode is On")

# ***** Open and connect to the BIOT SQL Database *****
try:
    conn = sqlite3.connect('biot.db')
    curs = conn.cursor()
    if (debug == 1): print ("Opened connection to biot.db database")

except:
    print ("Error connecting to the Database", sys.exc_info()[0])
    raise

# ***** Reset all Nodes to an Inactive Status *****
if (debug == 1): print("Setting all Node Status' to Inactive at Startup")
conn.execute('''UPDATE Node SET Node_Status = "Inactive"''')
conn.commit()

if (debug == 1): print("  -> Done")

# ***** Process Event on connection to MQTT server and ensure subscribtion to /RIOT2/SensorData Topic *****

def on_connect(client, userdata, flags, rc):                                                                   
    if (debug == 1): print("Connected to biot.db.  Result code = "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    client.subscribe("/RIOT2/SensorData")

# ***** Callback function to process the data published to the /RIOT2/SesorData Topic *****
def on_message(client, userdata, msg):
    node_Data = msg.payload.decode("utf-8")
    print(msg.topic+" -> ["+node_Data, "]")

    # Parse each data field from the record
    nodeType        = node_Data[3:8]
    macAddress      = node_Data[9:26]
    nodeId          = node_Data[3:26]
    swVersion       = node_Data[30:35]
    temperature     = node_Data[39:44]
    humidity        = node_Data[48:53]
    pressure        = node_Data[57:62]
    sequence        = node_Data[66:72]
    analog1         = node_Data[76:80]
    digital1        = node_Data[84:85]
    digital2        = node_Data[89:90]

    print ("				  Node Data")
    print ("				  ===========")
    print ("	Node Type 		= ", nodeType)
    print ("	MAC Address 		= ", macAddress)
    print ("	Node ID 		= ", nodeId)
    print ("	Software Version	= ", swVersion)
    #    print ("	DateTime 		= ")
    print ("	Temperature	        = ", temperature)
    print ("	Humidity 		= ", humidity)
    print ("	Pressure        	= ", pressure)
    print ("	Sequence 		= ", sequence)
    print ("	Analog 1 		= ", analog1)
    print ("	Digital 1 		= ", digital1)
    print ("	Digital 2 		= ", digital2)

    # Insert RIOT2 data into the Sensor_Data Table
    try:
        if (debug == 1): print ("Inserting Sensor Data into Database")
        conn.execute('''INSERT INTO Sensor_Data (Node_ID, Temperature, Humidity, Pressure, Sequence) \
        VALUES (?,?,?,?,?)''', (nodeId, temperature, humidity, pressure, sequence));
        if (debug == 1): print("  -> Done")

    except:
        print("A problem was experienced updating the Sensor_Data Table", sys.exc_info()[0])
        raise
    
    # Update or Insert Node Table from RIOT2 data
    try:
        if (debug == 1): print("Checking if Node exists in Table for ID: ", nodeId)
        curs.execute('SELECT count(*) FROM Node WHERE Node_ID = ?', (nodeId,));

        data=curs.fetchone()[0]
    
        if (data == 0):
            if (debug == 1): print("Node NOT in table.  INSERTING data into Node Table")
            curs.execute('''INSERT INTO Node (Node_ID, Node_Type, MAC_Address, SW_Version, Node_Status) \
            VALUES (?,?,?,?,"Active")''', (nodeId, nodeType, macAddress, swVersion));
            if (debug == 1): print("  -> Done")
        else:
            if (debug == 1): print("Node EXISTS in table. UPDATING Node Table")
            curs.execute('''UPDATE Node SET Node_Type = ?, MAC_Address = ?, SW_Version = ?, Node_Status = "Active" WHERE Node_ID = ?''',
                           (nodeType, macAddress, swVersion, nodeId));
            if (debug == 1): print("  -> Done")
        
    except:
        print("A problem was experienced updating the Node Table", sys.exc_info()[0])
        raise

    # Commit the updates to the db
    if (debug == 1): print("Committing table updates to database")
    conn.commit()
    if (debug == 1): print("  -> Done")

    
# ***** Connect to MQTT server *****
client = mqtt.Client()                  # Instantiate the MQTT client
client.on_connect = on_connect          # Set the function executed once a connection is made to the MQTT server
client.on_message = on_message          # Set the Callback function for a subscribed message
client.connect("127.0.0.1", 1883, 60)   # Connect to the MQTT server                                                                                                 

# ***** Main Program Loop that runs continuously processing received messages or a <cntrl>c is hit
try:
    client.loop_forever()                   # The client will loop here forever and process subscribed messages.
                                            # The loop ends when client.disconnect is called
except:
    print("\n***** Closing the Program *****", sys.exc_info()[0])

# ***** Close the program gracefully
print ("  -> Closing the database connection")
conn.close()

print ("  -> Closing the MQTT connection")
client.disconnect()


