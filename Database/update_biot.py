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
import paho.mqtt.client as mqtt

# ============================================= DEFINED FUNCTIONS =============================================

# ***** Process Event on connection to MQTT server and ensure subscribtion to /RIOT2/SensorData Topic *****
def on_connect(client, userdata, flags, rc):                                                                   
    if (debug == 1): print("Connected to MQTT Server.  Result code = "+str(rc))

    # Reconnect Subscribtion when a connection is made to the MQTT Server
    client.subscribe("/RIOT2/SensorData")


# ***** Callback function to process the data published to the /RIOT2/SesorData Topic *****
def on_message(client, userdata, msg):
    node_Data = msg.payload.decode("utf-8")
    print ("************************ Message Received on MQTT Topic /RIOT2/SensorData ************************\n")
    print("  ->", node_Data, "<-")        # Print out the Message Payload
    print(" ")

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

    # Get current time fo rthe time-stamp (will use Unix Time)
    currentTime = int(time.time())

    # Insert RIOT2 data into the Sensor_Data Table
    try:
        if (debug == 1): print("Inserting Sensor Data into Database")
        conn.execute('''INSERT INTO Sensor_Data (Node_ID, Date_Time, Temperature, Humidity, Pressure, Sequence) \
        VALUES (?,?,?,?,?,?)''', (nodeId, currentTime, temperature, humidity, pressure, sequence));
        if (debug == 1): print("  -> Done")

    except:
        print("A problem was experienced updating the Sensor_Data Table", sys.exc_info()[0])
        raise
    
    # Update or Insert Node Table from RIOT2 data
    try:
        if (debug == 1): print("Checking if data exists in Table for Node: ", nodeId)
        curs.execute('SELECT count(*) FROM Node WHERE Node_ID = ?', (nodeId,));

        data=curs.fetchone()[0]
    
        if (data == 0):
            if (debug == 1): print("  -> Node NOT in table.  INSERTING data into Node Table")
            curs.execute('''INSERT INTO Node (Node_ID, Node_Type, MAC_Address, SW_Version, Node_Status) \
            VALUES (?,?,?,?,"Active")''', (nodeId, nodeType, macAddress, swVersion));
            if (debug == 1): print("    -> Done")
        else:
            if (debug == 1): print("  -> Node EXISTS in table. UPDATING Node Table")
            curs.execute('''UPDATE Node SET Node_Type = ?, MAC_Address = ?, SW_Version = ?, Node_Status = "Active" WHERE Node_ID = ?''',
                           (nodeType, macAddress, swVersion, nodeId));
            if (debug == 1): print("    -> Done")
        
    except:
        print("A problem was experienced updating the Node Table", sys.exc_info()[0])
        raise

    # Commit the updates to the db
    if (debug == 1): print("Committing table updates to database")
    conn.commit()
    if (debug == 1): print("  -> Done")


    # Read back the last written Sensor Data record and compare to what came in from the Node
    try:
        cursor2 = conn.execute('''SELECT Node_ID, Date_Time, Temperature, Humidity, Pressure, Sequence FROM Sensor_Data
        WHERE ROWID = (SELECT MAX(ROWID) FROM Sensor_Data)''');

    except:
        print("A problem was experienced reading from the Sensor_Data Table", sys.exc_info()[0])
        raise

    for row in cursor2:
        print("		    Input Data                  Database Output")
        print("		    =========================   =======================")
        print("SENSOR DATA")
        print("  Node ID          = ", nodeId, "   ", row[0])
        print("  Date & Time 	   = ", time.strftime("%Y/%m/%d - %H:%M:%S", time.localtime(currentTime)), "     ", time.strftime("%Y/%m/%d - %H:%M:%S", time.localtime(row[1])))
        print("  Temperature	   = ", temperature, "                      ", row[2])
        print("  Humidity 	   = ", humidity, "                      ", row[3])
        print("  Pressure         = ", pressure, "                     ", row[4])
        print("  Sequence 	   = ", sequence, "                        ", row[5])


    # Read back the last written Node Data record and compare to what came in from the Node
    try:
        cursor2 = conn.execute('''SELECT Node_ID, Node_Type, MAC_Address, SW_Version FROM Node WHERE Node_ID =?''', (nodeId,));

    except:
        print("A problem was experienced reading from the Node Table", sys.exc_info()[0])
        raise

    for row in cursor2:
        print("\nNODE DATA")
        print("  Node ID 	   = ", nodeId, "   ", row[0])
        print("  Node Type 	   = ", nodeType,"                     ", row[1])
        print("  MAC Address 	   = ", macAddress, "         ", row[2])
        print("  Software Version = ", swVersion,  "                    ", row[3])
        print("\n\n")

# ====================== Main Program ============================
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
    if (debug == 1): print("Opened connection to biot.db database")

except:
    print("Error connecting to the Database", sys.exc_info()[0])
    raise

# ***** Reset all Nodes to an Inactive Status *****
if (debug == 1): print("Setting all Node Status' to Inactive at Startup")
conn.execute('''UPDATE Node SET Node_Status = "Inactive"''')
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
print("  -> Closing the database connection")
conn.close()

print("  -> Closing the MQTT connection")
client.disconnect()


