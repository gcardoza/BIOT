#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('BIOT_Base.db')
print "Opened BIOT database successfully";

conn.execute('''CREATE TABLE Node
	(Node_ID 	INT,
	Node_Type	TEXT,
	SW_Version	TEXT,
	MAC_Address	TEXT,
	Serial_Port	TEXT,
	Node_Location	TEXT,
	Node_Status	TEXT);''')
print "Node Table created successfully";

conn.execute('''CREATE TABLE Sensor_Data
	(Node_ID	INT,
	Date_Stamp	DATE,
	Time_Stamp	TIME,
	DHT22_Temperature	REAL,
	DHT22_Humidity	REAL,
	BMP180_Temperature	REAL,
	BMP180_Pressure	REAL,
	Moisture_1	INT,
	Moisture_2	INT,
	Moisture_3	INT,
	Sequence        INT);''')
print "Data Table created successfully";

conn.execute('''CREATE TABLE Alert
	(Date_Stamp	DATE,
	TIME_Stamp	TIME,
	Alert_Source	TEXT,
	Alert_Message	TEXT,
	Alert_Sent	TEXT,
	Alert_Status	TEXT);''')
print "Alert Table created successfully";

conn.execute('''CREATE TABLE User
	(User_Name	TEXT,
	Email_Address	TEXT,
	Mobile_Number	TEXT,
	User_Status	TEXT);''')
print "User Table created successfully";

conn.close()

