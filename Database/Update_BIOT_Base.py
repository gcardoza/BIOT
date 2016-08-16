#!/usr/bin/python3

# Project:	BIOT Base Monitoring Station - Reads data from the RIOT devices
# Author:	Geofrey Cardoza
# Company:	Excaliber Inc. (c)
# Baseline:	June 28th, 2016
# Revision:	August 15th, 2016  v1.0
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
#	M1:	3			Moisture Level 1 (%)
#	M2:	3			Moisture Level 2 (%)
#	M3:	3			Moisture Level 3 (%)
#       SE:     6                       Transmission sequence number
 
import serial
import sys
import sqlite3
import time
import datetime

debug = 0
activeNodeNumber = []
activeNodePort = []
availableNodeData = [0,0,0,0,0,0,0,0]
serialPort = []

# Check for command line arguments and if debug is on -d
if (len(sys.argv) >= 2):
    x = sys.argv[1]
    if (x == "-d"):
        debug = 1
        print("Debug Mode is On")
    
# ***** Open and connect to the BIOT SQL Database *****
try:
    conn = sqlite3.connect('BIOT_Base.db')
    if (debug == 1): print ("Opened connection to BIOT_Base database")
    
except:
    print ("Error connecting to the Database", sys.exc_info()[0])
    raise

# **** Open the serial device for reading data from the remote devices ***** 
try:
    #Retriev all Active Nodes from Node Table and their serial ports
    maxNodes = 0
    cursor = conn.execute("SELECT Node_ID, Serial_Port from Node WHERE Node_Status = ('Active')");
    for row in cursor:
        activeNodeNumber.append(row[0])
        activeNodePort.append(row[1])
        maxNodes += 1
    if (debug == 1) : print("Total number of Active Nodes = ", maxNodes)
    
    # Open the Serial Ports for each Active Node
    n = 0
    while n < maxNodes:
        if (debug == 1) : print("Opening Serial Port ", activeNodePort[n], "for Node:", activeNodeNumber[n])
        serialPort.append(serial.Serial(activeNodePort[n], timeout=5))
        n += 1

except:
    print("Could not open the serial port to receive data", sys.exc_info()[0])
    raise
        
# ***** Main Program Loop - Process 1 data record from each node and move to next node *****
currentNode = 0   #start loop on the first node
while True:
    try:    # Check if there is data to read from the node port
        if (debug == 1) : print("Reading Data from Node:", activeNodeNumber[currentNode])
        availableNodeData[currentNode] = serialPort[currentNode].inWaiting()
        if (debug == 1) : print("Bytes available on Node = ", availableNodeData[currentNode])

        # Read data if there is data available
        if(availableNodeData[currentNode] != 0):
            record = serialPort[currentNode].readline()

    except:  # *?* Handle each error condition appropriately
        if (debug ==1) : print("Could not read data from serial port", sys.exc_info()[0])
        availableNodeData[currentNode] = 0
        continue

    # 1. Process current record if there is data available
    if(availableNodeData[currentNode] != 0):
        nodeData = record.decode("utf-8")	# Convert the data from binary to a string
        if (debug == 1) : print ("Input record received from Node ->", nodeData)

        # Ensure this is a valid data record (header= RIOT1) and not a debug statement
        R1 = nodeData[0:5]
        if (R1 == "RIOT1"):
            # 2. Parse each data field from the record
            if (debug == 1) : print ("Parsing Node Data")
            SW = nodeData[6:11]
            ID = nodeData[16:18]
            DS = nodeData[23:33]
            TS = nodeData[34:42]
            DT = nodeData[47:52]
            DH = nodeData[57:62]
            BT = nodeData[67:72]
            BP = nodeData[77:82]
            M1 = nodeData[87:90]
            M2 = nodeData[95:98]
            M3 = nodeData[103:106]
            SE = nodeData[111:117]
               
            # Insert Parsed Node data into the Database
            try:
                if (debug == 1) : print ("Inserting Data into Database")
                conn.execute('''INSERT INTO Sensor_Data (Node_ID, Date_Stamp, Time_Stamp,
                DHT22_Temperature, DHT22_Humidity, BMP180_Temperature, BMP180_Pressure,
                Moisture_1, Moisture_2, Moisture_3, Sequence) \
                VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (ID, DS, TS, DT, DH, BT, BP, M1, M2, M3, SE));

                # ?*? Update Node Table with Software Version
                
            except:
                # Insert failed - so Rollback the Insert and close the serial port
                print ("Rolling back db insert")
                cursor.rollback()

                print ("Closing db connection")
                conn.close()    # close database connection

                print("Closing all serial ports")
                n = 0
                while (n < maxNodes):
                    serialPort[n].close()
                    n +=1
                
                print("Error Inserting data into the Database", sys.exc_info()[0])
                raise

            #  Write the data and committ it to the database
            conn.commit()
                        
            # Read back the last written record and print contents
            try:
                cursor = conn.execute('''SELECT Node_ID, Date_Stamp, Time_Stamp, DHT22_Temperature,
                DHT22_Humidity, BMP180_Temperature, BMP180_Pressure, Moisture_1, Moisture_2,
                Moisture_3, Sequence from Sensor_Data WHERE ROWID = (SELECT MAX(ROWID) FROM Sensor_Data)''');
            except:
                print("Error Reading the Database", sys.exc_info()[0])
                raise

            for row in cursor:
                if (debug == 1): print ("Reading Record back from Database")
                print ("				  Node Data	Database Output")
                print ("				  ===========	===============")
                print ("	Node_ID 		= ", ID, "		",row[0])
                print ("	Device_Type 		= ", R1, "	","-----")
                print ("	Software Version	= ", SW, "	","-----")
                print ("	Date_Stamp 		= ", DS, "	",row[1])
                print ("	Time_Stamp 		= ", TS, "	",row[2])			
                print ("	DHT22_Temperature	= ", DT, "	",row[3])
                print ("	DHT22_Humidity 		= ", DH, "	",row[4])
                print ("	BMP180_Temperature 	= ", BT, "	",row[5])
                print ("	BMP180_Pressure 	= ", BP, "	",row[6])
                print ("	Moisture_1 		= ", M1, "	        ",row[7])
                print ("	Moisture_2 		= ", M2, "	        ",row[8])
                print ("	Moisture_3 		= ", M3, "	        ",row[9])
                print ("	Sequence 		= ", SE, "	",row[10],"\n")			

    # Increment to next active node if at max then start over
    currentNode += 1
    if (currentNode == maxNodes):
        #check if there was data available on any node
        n = 0
        count = 0
        while n < maxNodes:
            count += availableNodeData[n]
            n += 1
        if (debug == 1) : print("Data Count = ", count)

        if(count == 0):
            if (debug == 1) : print("No data available on any active port. Sleeping for 20 seconds")
            time.sleep(20)
        currentNode = 0
