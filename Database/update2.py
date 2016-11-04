#!/usr/bin/python3

# Project:	BIOT Home IOT Base Station - Updates SQL database with RIOT2 published SensorData
# Author:	  Geofrey Cardoza
# Company:	Excaliber Inc. (c)
# Baseline:	June 28th, 2016
# Revision:	October 31st, 2016  v1.3
# Change:   Normalized RioT2 data, Added MQTT Security

import serial
import sys
import sqlite3
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ============================================= DEFINED FUNCTIONS =============================================

# ***** SEND THE ALERT DATA TO ALL ENABLED USERS *****
def send_NodeAlert(AlertMessage):
    if(debug >= 1): print("\nsend_NodeAlert: ", AlertMessage)
    
    #to and from addresses
    fromAddress = "biot.riot@gmail.com"
    
    if(debug > 1): print ("  -> Connecting to smtp server")
    # send the email
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(fromAddress,"Pinot1991$")

    if(debug > 1): print("  -> Sending Alert Email to every Enabled User in biot database")
    cursor = conn.execute("SELECT Email_Address FROM User WHERE User_Status = 'Enabled'");
    for row in cursor:
        toAddress  = row[0]
        
        if(debug > 1): print("     -> Composing Alert Email MIME message")
        msg = MIMEMultipart()
        msg['From'] = fromAddress
        msg['To'] = toAddress
        msg['Subject'] = "*** RioT Alert Message ***"
        msg.attach(MIMEText(AlertMessage, 'plain'))
        text = msg.as_string()

        if(debug >= 1): print("     -> Sending Alert EMail To: ", toAddress)
        server.sendmail(fromAddress, toAddress, text)
    server.quit()
    if(debug > 1): print ("\n<- send_NodeAlert:  Done")    
    
# ***** Process a NodeAlert Message *****
def process_NodeAlert(nodeLocation, alertValue, alertId, updateDelay):
    
    if(debug > 1): print("\nprocess_NodeAlert: Alert Triggered\n  -> Node: ", nodeLocation,
    " Threshold Exceeded: ", alertValue, " AlertId: ", alertId, " UpdateDelay: ", updateDelay)
   
    currentTime = int(time.time())
    
    # Check if an Alert has already been sent on this condition for this Node within updateDelay
    if(debug > 1): print("  -> Checking if a similar Alert has already been sent to this Node")
    cursor = conn.execute("SELECT MAX(Date_Time) FROM Alert_Status WHERE Node_Location = ? AND Alert_ID = ?", (nodeLocation, alertId))
    data=cursor.fetchone()[0]

    if(data == None):
        print("     -> No previous Alert message found ")
        okToSend = 1        
    else: 
        age = currentTime - data
        print("     -> Previous Alert Record found,  Age: ", age)
        if(age > updateDelay): okToSend = 1
        else: okToSend = 0
        
    # Only Send Alert if a similar alert was sent to this Node more than the delay period 
    if(okToSend == 1):   
        if(debug > 1): print("  -> Creating Alert Message to Send to Node")
        # Get the text for the Alert from the Alert_Messages table
        curs = conn.execute('''SELECT Alert_Message FROM Alert_Messages WHERE Alert_ID =?''', (alertId,));
        for row in curs: alertMessage = row[0]
    
        message  = time.strftime("%Y/%m/%d - %H:%M:%S", time.localtime(currentTime))
        message += " - "
        message += nodeLocation
        message += " - "
        message += alertMessage
        message += " "
        message += str(alertValue)
        print("     -> *** ", message)
        
        #Insert new Alert message into Alert_Status table
        if(debug > 1): print("  -> Inserting new Alert Entry into Alert_Status Table")
        curs.execute('''INSERT INTO Alert_status (Date_Time, Node_Location, Alert_ID, Alert_Message, Alert_Status) \
                        VALUES (?,?,?,?,"Active")''', (currentTime, nodeLocation, alertId, message));
        conn.commit()

        # Send Alert message
        if(debug > 1): print("  -> Alert Message: ", message)
        send_NodeAlert(message)

    if(debug > 1): print("\n<- process_NodeAlert: Done")

# ***** PROCESS THE NODE DATA PUBLISHED TO THE /RioT/Status TOPIC *****
def process_SensorData(node_Data):
    if(debug > 1): print("process_SensorData: Processing data from RioT2")

    # ***** Parse each data field from the record *****
    nodeType        = node_Data[3:8]
    macAddress      = node_Data[9:26]
    nodeId          = node_Data[3:26]
    swVersion       = node_Data[30:35]
    sequence        = node_Data[39:45]
    temperature     = node_Data[53:58]
    humidity        = node_Data[62:67]
    pressure        = node_Data[71:76]
    analog          = node_Data[80:84]
    alarm           = node_Data[88:89]
    digital1        = node_Data[93:94]

    # Get current time fo rthe time-stamp (will use Unix Time)
    currentTime = int(time.time())

    # ***** INSERT RIOT DATA INTO THE SENSOR_DATA TABLE *****
    try:
        if (debug > 1): print("  -> Inserting Sensor Data into Database")
        conn.execute('''INSERT INTO Sensor_Data (Node_ID, Date_Time, Temperature, Humidity, Pressure, Sequence, Analog, Alarm, Digital_1) \
        VALUES (?,?,?,?,?,?,?,?,?)''', (nodeId, currentTime, temperature, humidity, pressure, sequence, analog, alarm, digital1));
        if (debug > 1): print("     -> Done\n")

    except:
        print("A problem was experienced updating the Sensor_Data Table", sys.exc_info()[0])
        raise
    
    # ***** UPDATE OR INSERT NODE TABLE FROM RIOT DATA *****
    try:
        if (debug > 1): print("  -> Checking if data exists in Table for Node: ", nodeId)
        curs.execute('SELECT count(*) FROM Node WHERE Node_ID = ?', (nodeId,));

        data=curs.fetchone()[0]
    
        if (data == 0):
            if (debug > 1): print("     -> Node NOT in table.  INSERTING data into Node Table")
            curs.execute('''INSERT INTO Node (Node_ID, Node_Type, MAC_Address, SW_Version, Node_Status, Node_Location) \
            VALUES (?,?,?,?,"Active","Location Not Defined")''', (nodeId, nodeType, macAddress, swVersion));
            if (debug > 1): print("        -> Done\n")
        else:
            if (debug > 1): print("     -> Node EXISTS in table. UPDATING Node Table")
            curs.execute('''UPDATE Node SET Node_Type = ?, MAC_Address = ?, SW_Version = ?, Node_Status = "Active" WHERE Node_ID = ?''',
                           (nodeType, macAddress, swVersion, nodeId));
            if (debug > 1): print("        -> Done\n")
        
    except:
        print("A problem was experienced updating the Node Table", sys.exc_info()[0])
        raise

    # Commit the updates to the db
    if (debug > 1): print("  -> Committing table updates to database")
    conn.commit()
    if (debug > 1): print("     -> Done\n")

    # Read back the last written Sensor Data record and compare to what came in from the Node
    cursor = conn.execute('''SELECT Node_ID, Date_Time, Temperature, Humidity, Pressure, Sequence, Analog, Alarm, Digital_1 FROM Sensor_Data
        WHERE ROWID = (SELECT MAX(ROWID) FROM Sensor_Data)''');

    for row in cursor:
        db_nodeId       = row[0]
        db_time         = row[1]
        db_temperature  = row[2]
        db_humidity     = row[3]
        db_pressure     = row[4]
        db_sequence     = row[5]
        db_analog       = row[6]
        db_alarm        = row[7]
        db_digital1     = row[8]
    
    # Check if the Node has an operational Weather Sensor (if Temp = 999 then no working sensor was detected)
    if(db_temperature == 999.0):
        if(debug > 1): print("  -> No weather sensor was detected for this Node")
        weatherSensorPresent = 0
    else:
        if(debug > 1): print("  -> A weather sensor was detected for this Node")
        weatherSensorPresent = 1
        
    if(debug > 1):
        print("\n  -> Verifying data from database\n")
        print("  		    Input Data                  Database Output")
        print("	  	    =========================   =======================")
        print("  SENSOR DATA")
        print("    Node ID          = ", nodeId, "   ", db_nodeId)
        print("    Date & Time      = ", time.strftime("%Y/%m/%d - %H:%M:%S", time.localtime(currentTime)),
              "     ", time.strftime("%Y/%m/%d - %H:%M:%S", time.localtime(db_time)))
        print("    Sequence         = ", sequence, "                        ", db_sequence)
        print("    Temperature      = ", temperature, "                      ", db_temperature)
        print("    Humidity         = ", humidity, "                      ", db_humidity)
        print("    Pressure         = ", pressure, "                     ", db_pressure)
        print("    Analog           = ", analog, "                        ", db_analog)
        print("    Alarm            = ", alarm, "                         ", db_alarm)
        print("    Digital_1        = ", digital1, "                         ", db_digital1)
        
    # Read back the last written Node Data record and compare to what came in from the Node
    cursor = conn.execute('''SELECT Node_ID, Node_Type, MAC_Address, SW_Version, Node_Location FROM Node WHERE Node_ID =?''', (nodeId,));

    for row in cursor:
        db_nodeId = row[0]
        db_nodeType = row[1]
        db_macAddress = row[2]
        db_swVersion = row[3]
        nodeLocation = row[4]
    
    if(debug > 1):
        print("\n  NODE DATA")
        print("    Node ID          = ", nodeId, "   ", db_nodeId)
        print("    Node Type        = ", nodeType,"                     ", db_nodeType)
        print("    MAC Address      = ", macAddress, "         ", db_macAddress)
        print("    Software Version = ", swVersion,  "                    ", db_swVersion)
        print("    Node Location    =  ---                        ", nodeLocation)
        print(" ")
     
    # ***** SEND CURRENT TEMPERATURE TO THE HOME ASSISTANT LISTENING MQTT TOPIC *****
    # Only Send data if the Node has a working weather sensor
    if(weatherSensorPresent): 
        if(debug >= 1): print("  -> Sending Data to Home Assistant for Node Location: ", nodeLocation)
        data = json.dumps({"Temperature": temperature, "Humidity": humidity, "Pressure": pressure})
        if(debug >= 1): print ("  -> Data:", data)
        
        if(nodeLocation == "1. Main Floor") : client.publish("/BioT/SensorData/main", data)
        elif(nodeLocation == "2. Upstairs") : client.publish("/BioT/SensorData/upstairs", data)
        elif(nodeLocation == "3. Basement") : client.publish("/BioT/SensorData/basement", data)
        elif(nodeLocation == "4. Attic")    : client.publish("/BioT/SensorData/attic", data)
        elif(nodeLocation == "5. Outside")  : client.publish("/BioT/SensorData/outside", data)
        else: print("     -> *** Unknown Location: ", nodeLocation)

    # ***** CHECK FOR AND PROCESS ALERT CONDITIONS *****
    if(debug > 1): print("\n  -> Checking if any Alert conditions have been met")
    
    # Check if an Alert record exists for this Node (i.e this is a new node and hasn't been setup) 
    curs.execute('SELECT count(*) FROM Alert_Rules WHERE Node_ID = ?', (nodeId,));
    data=curs.fetchone()[0]
    if (data != 0):
    
        # Read the Alert thresholds for this Node
        if(debug > 1): print("     -> Reading the Alert Thresholds for this Node")
      
        cursor = conn.execute('''SELECT Low_Temperature, High_Temperature, Low_Humidity, High_Humidity, 
                              Low_Pressure, High_Pressure, Alarm_Value, Update_Delay FROM Alert_Rules WHERE Node_ID =?''', (nodeId,));
        for row in cursor:
            lowTemp   = row[0]
            highTemp  = row[1]
            lowHum    = row[2]     
            highHum   = row[3]
            lowPres   = row[4]
            highPres  = row[5]
            alarmVal  = row[6]
            updateDel = row[7]
            if(debug > 1): print("     -> LT: ", lowTemp, " HT: ", highTemp, " LH: ", lowHum, " HH: ", highHum,
                                " LP: ", lowPres, " HP: ", highPres, " AL: ", alarmVal, " UD: ", updateDel)
        
        # Only procees weather Alerts if the Node has a working weather sensor
        if(weatherSensorPresent):
            if(debug >1): print("     -> Processing Weather Related Alerts")
            # Check if Temperature thresholds have been exceeded
            if(db_temperature <= lowTemp): process_NodeAlert(nodeLocation, lowTemp, 'TemperatureLow', updateDel)
            elif(db_temperature >= highTemp): process_NodeAlert(nodeLocation, highTemp, 'TemperatureHigh', updateDel)
            
            # Check if Humidity thresholds have been exceeded
            if(db_humidity <= lowHum): process_NodeAlert(nodeLocation, lowHum, 'HumidityLow', updateDel)
            elif(db_humidity >= highHum): process_NodeAlert(nodeLocation, highHum, 'HumidityHigh', updateDel)
            
            # Check if Pressure thresholds have been exceeded
            if(db_pressure <= lowPres): process_NodeAlert(nodeLocation, lowPres, 'PressureLow', updateDel)
            elif(db_pressure >= highPres): process_NodeAlert(nodeLocation, highPres, 'PressureHigh', updateDel)
        
        # Check if an Alarm has been triggered
        if(debug >1): print("     -> Processing Alarm Related Alerts")
        if(db_alarm >= alarmVal): process_NodeAlert(nodeLocation, alarmVal, 'WaterLeak', updateDel)

    else:
        if(debug > 1): print("     -> No Alert_Rules records found.  Not processing Alerts for this Node.")

    if(debug > 1): print("\n<- process_SensorData: Done")
        
# ***** PROCESS THE IRRIGATION STATUS PUBLISHED TO THE /RioT/Status TOPIC *****
def process_IrrigationStatus(node_Data):
    if(debug > 1): print("process_IrrigationStatus: Processing data from RioT3")

    # ***** Parse each data field from the record *****
    nodeType        = node_Data[3:8]
    macAddress      = node_Data[9:26]
    nodeId          = node_Data[3:26]
    swVersion       = node_Data[30:35]
    sequence        = node_Data[39:45]
    activeZone      = node_Data[51:52]
    zoneOnTime      = node_Data[53:58]

    # Get current time for the time-stamp (will use Unix Time)
    currentTime = int(time.time())
    
    if(debug > 1):
        print("\n  -> Verifying data from database\n")
        print("  		    Input Data                  Database Output")
        print("	  	    =========================   =======================")
        print("  SENSOR DATA")
        print("    Node ID          = ", nodeId, "   ", nodeId)
        print("    Date & Time      = ", time.strftime("%Y/%m/%d - %H:%M:%S", time.localtime(currentTime)),
              "     ", time.strftime("%Y/%m/%d - %H:%M:%S", time.localtime(currentTime)))
        print("    Sequence         = ", sequence, "                        ", sequence)
        print("    Active Zone      =     ", activeZone, "                          ", activeZone)
        print("    Zone On-Time     = ", zoneOnTime, "                      ", zoneOnTime)

    # ***** INSERT RIOT3 DATA INTO IRRIGATION_STATUS TABLE *****
    try:
        if (debug > 1): print("  -> Inserting Irrigation Status Data into Database")
        conn.execute('''INSERT INTO Zone_Status (Node_ID, Zone_ID, Date_Time, Zone_Status, Zone_OnTime) \
        VALUES (?,?,?,'On',?)''', (nodeId, activeZone, currentTime, zoneOnTime));
        if (debug > 1): print("     -> Done\n")

    except:
        print("A problem was experienced updating the Sensor_Data Table", sys.exc_info()[0])
        raise


        # ***** UPDATE OR INSERT NODE TABLE FROM RIOT DATA *****
    try:
        if (debug > 1): print("  -> Checking if data exists in Table for Node: ", nodeId)
        curs.execute('SELECT count(*) FROM Node WHERE Node_ID = ?', (nodeId,));

        data=curs.fetchone()[0]
    
        if (data == 0):
            if (debug > 1): print("     -> Node NOT in table.  INSERTING data into Node Table")
            curs.execute('''INSERT INTO Node (Node_ID, Node_Type, MAC_Address, SW_Version, Node_Status, Node_Location) \
            VALUES (?,?,?,?,"Active","Location Not Defined")''', (nodeId, nodeType, macAddress, swVersion));
            if (debug > 1): print("        -> Done\n")
        else:
            if (debug > 1): print("     -> Node EXISTS in table. UPDATING Node Table")
            curs.execute('''UPDATE Node SET Node_Type = ?, MAC_Address = ?, SW_Version = ?, Node_Status = "Active" WHERE Node_ID = ?''',
                           (nodeType, macAddress, swVersion, nodeId));
            if (debug > 1): print("        -> Done\n")
        
    except:
        print("A problem was experienced updating the Node Table", sys.exc_info()[0])
        raise

    # Commit the updates to the db
    if (debug > 1): print("  -> Committing table updates to database")
    conn.commit()
    if (debug > 1): print("     -> Done")

  
# ***** PROCESS EVENT ON CONNECTION TO MQTT SERVER AND ENSURE SUBSCRIBTION TO /RIOT2/SENSORDATA TOPIC *****
def on_connect(client, userdata, flags, rc):                                                                   
    if (debug > 1): print("on_connect:  Connected to MQTT Server.  Result code = "+str(rc))

    # Reconnect Subscribtion when a connection is made to the MQTT Server
    client.subscribe("/RioT/Status")

    if (debug > 1): print("\n<- on_connect:  Done subscribing to /RioT/Status Topics")
    
# ***** CALLBACK FUNCTION TO PROCESS MQTT DATA RECEIVED ON SUBSCRIBED TOPICS *****
def on_message(client, userdata, msg):
    mqtt_Data = msg.payload.decode("utf-8")
    
    if(debug >= 1): print("\n\n************************ Message Received on Subscribed MQTT Topic ************************\n")
    if(debug >= 1): print("on_message:  Message Topic :",msg.topic, ", Message Length: ", len(mqtt_Data), "\n  Payload ->", mqtt_Data, "<-\n") 

    # Call appropriate Processor determined by message Topic
    messageType = mqtt_Data[46:49]
    if(debug >= 1): print("on_message: Subscribed Message Type:",)
    if(msg.topic == "/RioT/Status" and len(mqtt_Data) >=94 and messageType == "SD:"):  process_SensorData(mqtt_Data)
    elif(msg.topic == "/RioT/Status" and len(mqtt_Data) >=58 and messageType == "IS:"):  process_IrrigationStatus(mqtt_Data)
    else: 
        if(debug > 1): print ("Message Not Processed - Unrecognized")

    if(debug >= 1): print("\n<- on_message:  Done")
# ============================================= MAIN PROGRAM ==================================================
debug = 0

# Check for command line arguments and if debug is on -d
if(len(sys.argv) >= 2):
    x = sys.argv[1]
    if(x == "-d1"): debug = 1
    elif(x == "-d2"): debug = 2
if(debug > 0): print("Debug Mode is On")

# ***** Open and connect to the BIOT SQL Database *****
try:
    conn = sqlite3.connect('biot.db')
    curs = conn.cursor()
    if(debug > 1): print("Opened connection to biot.db database")

except:
    print("Error connecting to the Database", sys.exc_info()[0])
    raise

# ***** Reset all Nodes to an Inactive Status *****
if(debug > 1): print("Setting all Node Status' to Inactive at Startup")
conn.execute('''UPDATE Node SET Node_Status = "Inactive"''')
conn.commit()

if(debug > 1): print("  -> Done")

# ***** Connect to MQTT server *****
client = mqtt.Client()                  # Instantiate the MQTT client
client.on_connect = on_connect          # Set the function executed once a connection is made to the MQTT server
client.on_message = on_message          # Set the Callback function for a subscribed message
client.username_pw_set("biot", "excaliber") # Set MQTT connection user ID and Password
client.connect("127.0.0.1", 1883, 60)   # Connect to the MQTT server                                                                                                 

# ***** Main Program Loop that runs continuously processing received messages or a <cntrl>c is hit
#try:
client.loop_forever()                   # The client will loop here forever and process subscribed messages.
                                            # The loop ends when client.disconnect is called
#except:
print("\n***** Closing the Program *****", sys.exc_info()[0])

# ***** Close the program gracefully
print("  -> Closing the database connection")
curs.close()
conn.close()

print("  -> Closing the MQTT connection")
client.disconnect()


