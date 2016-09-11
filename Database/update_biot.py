#!/usr/bin/python3

# Project:	BIOT Base Monitoring Station - Reads data from the RIOT2+ devices
# Author:	Geofrey Cardoza
# Company:	Excaliber Inc. (c)
# Baseline:	June 28th, 2016
# Revision:	August 15th, 2016  v1.0a
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
    print ("Opened connection to biot.db database")

except:
    print ("Error connecting to the Database", sys.exc_info()[0])
    raise

# ***** Process Event on connection to MQTT server and ensure subscribtion to /RIOT2/SensorData Topic *****

def on_connect(client, userdata, flags, rc):                                                                   
    print("Connected to biot.db.  Result code = "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    client.subscribe("/RIOT2/SensorData")

# ***** Callback function to process the data published to the /RIOT2/SesorData Topic *****
def on_message(client, userdata, msg):
    node_Data = msg.payload.decode("utf-8")
    print(msg.topic+" "+node_Data)

    # 2. Parse each data field from the record
    print ("Parsing Node Sensor Data")
    nodeType        = node_Data[3:8]
    macAddress      = node_Data[9:26]
    nodeId          = node_Data[3:26]
    softwareVersion = node_Data[30:35]
    temperature     = node_Data[39:44]
    humidity        = node_Data[48:53]
    pressure        = node_Data[57:62]
    analog1         = node_Data[66:70]
    digital1        = node_Data[74:75]
    digital2        = node_Data[79:80]
    sequence        = node_Data[84:90]

    print ("				  Node Data")
    print ("				  ===========")
    print ("	Node Type 		= ", nodeType)
    print ("	MAC Address 		= ", macAddress)
    print ("	Node ID 		= ", nodeId)
    print ("	Software Version	= ", softwareVersion)
    print ("	Date_Stamp 		= ")
    print ("	Time_Stamp 		= ")			
    print ("	Temperature	        = ", temperature)
    print ("	Humidity 		= ", humidity)
    print ("	Pressure        	= ", pressure)
    print ("	Analog 1 		= ", analog1)
    print ("	Digital 1 		= ", digital1)
    print ("	Digital 2 		= ", digital2)
    print ("	Sequence 		= ", sequence)			



# ***** Main code loop *****
client = mqtt.Client()                  # Instantiate the MQTT client
client.on_connect = on_connect          # Set the function executed once a connection is made to the MQTT server
client.on_message = on_message          # Set the Callback function for a subscribed message

client.connect("127.0.0.1", 1883, 60)   # Connect to the MQTT server                                                                                                 

client.loop_forever()                   # The client will loop here forever and process subscribed messages.
                                        # The loop ends when client.disconnect is called 
