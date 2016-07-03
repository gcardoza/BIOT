#!/usr/bin/python3

# Project:	BIOT Base Monitoring Station - Reads data from the RIOT devices
# Author:	Geofrey Cardoza
# Company:	Excaliber Inc. (c)
# Baseline:	June 28th, 2016
# Revision:	July 3rd, 2016  v0.7
#
# Input device:	/dev/rfconn1 through /dev/rfconn8 for all 8 RIOT1 devices
# Input Format: Field header(3), Data length and format, Description
#	RIOT1	5.0			Device Type
#	SW:	5.1			Node software version
#	ID:	2.0			Device ID
#	DS:	yyyymmdd		Date Stamp
#	TS:	hh:mm:ss		Time Stamp
#	DT:	5.1			DHT22 Temperature (C)
#	DH:	5.1			DHT22 Humidity (%)
#	BT:	5.1			BMP180 Temperature (C)
#	BP:	5.1			BMP180 Pressure (kPa)
#	M1:	5.1			Moisture Level 1 (%)
#	M2:	5.1			Moisture Level 2 (%)
#	M3:	5.1			Moisture Level 3 (%)
 
import serial
import sys
import sqlite3
import time

debug = 1

# 0. ***** Open and connect to the BIOT SQL Database *****
try:
    print("Opening connection to BIOT_Base Database")
    conn = sqlite3.connect('BIOT_Base.db')
    print ("Opened BIOT_Base database")
except:
    print ("Error connecting to the Database", sys.exc_info()[0])
    raise

# 1. ***** Open the serial device for reading data from the remote devices ***** 
try:
    print("Opening Bluetooth Serial Port")
    serialPort = serial.Serial('/dev/rfcomm1')
    print ("Opened the Bluetooth connection to Node 1\n")
except:
    print("Could not open the serial port to receive data", sys.exc_info()[0])
    raise
        
# 2. ***** Main Program Loop - Continuously read the serial device for Node data *****
while True:
    try:    # 3. ***** Read next record from the serial port
        print("Reading Node Data from Serial Port")
        record = serialPort.readline()
    except: # 3. 
        print("Could not read data from serial port", sys.exc_info()[0])
        time.sleep(60) # Wait 60 seconds and try again if a device has no data
        continue

    Node_Data = record.decode("utf-8")	# Convert the data from binary to a string
    print ("Input record received from Node")
    print (Node_Data, end="")

    # 4. Ensure this is a data record header= RIOT1 and not a debug statement
    R1 = Node_Data[0:5]
    if (R1 == "RIOT1"):
        # Parse each data field from the record
        print ("Parsing Node Data")
        SW = Node_Data[6:11]
        ID = Node_Data[16:18]
        DS = Node_Data[23:33]
        TS = Node_Data[34:42]
        DT = Node_Data[47:52]
        DH = Node_Data[57:62]
        BT = Node_Data[67:72]
        BP = Node_Data[77:82]
        M1 = Node_Data[87:92]
        M2 = Node_Data[97:102]
        M3 = Node_Data[107:112]
        SE = Node_Data[117:123]

        # 5. ***** Insert Parsed Node data into the Database *****
             #  For now I'm using the Pi date - when the Arduino has a RTC switch the update fields
        try:
            print ("Inserting Data into Database")
            conn.execute('''INSERT INTO Sensor_Data (Node_ID, Date_Stamp, Time_Stamp,
            DHT22_Temperature, DHT22_Humidity, BMP180_Temperature, BMP180_Pressure,
            Moisture_1, Moisture_2, Moisture_3) \
            VALUES (?,Date('now'),Time('now'),?,?,?,?,?,?,?)''', (ID, DT, DH, BT, BP, M1, M2, M3));
        except: # 5.
            # Insert failed - so Rollback the Insert and close the serial port
            cursor.rollback()
            serialPort.close()
            print("Error Inserting data into the Database", sys.exc_info()[0])
            raise

        #  Write the data and committ it to the database
        conn.commit()
                        
        # 6. Read back the last written record and print contents
        try:
            cursor = conn.execute('''SELECT Node_ID, Date_Stamp, Time_Stamp, DHT22_Temperature,
            DHT22_Humidity, BMP180_Temperature, BMP180_Pressure, Moisture_1, Moisture_2,
            Moisture_3 from Sensor_Data WHERE ROWID = (SELECT MAX(ROWID) FROM Sensor_Data)''');
        except: # 6.
            print("Error Reading the Database", sys.exc_info()[0])
            raise

        for row in cursor:
            print ("Reading Record back from Database")
            print ("				  Node Data	Database Output")
            print ("				  ===========	===============")
            print ("	Device_Type 		= ", R1, "	","-----")
            print ("	Node_ID 		= ", ID, "		",row[0])
            print ("	Date_Stamp 		= ", DS, "	",row[1])
            print ("	Time_Stamp 		= ", TS, "	",row[2])			
            print ("	DHT22_Temperature	= ", DT, "	",row[3])
            print ("	DHT22_Humidity 		= ", DH, "	",row[4])
            print ("	BMP180_Temperature 	= ", BT, "	",row[5])
            print ("	BMP180_Pressure 	= ", BP, "	",row[6])
            print ("	Moisture_1 		= ", M1, "	",row[7])
            print ("	Moisture_2 		= ", M2, "	",row[8])
            print ("	Moisture_3 		= ", M3, "	",row[9])
            print ("	Sequence 		= ", SE, "	","------")			
            print ("\n\n")

