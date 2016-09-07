#!/usr/bin/python3

import sqlite3

conn = sqlite3.connect('biot.db')
print ("Opened BIOT database successfully");

print ("Creating Tables");
conn.execute('''CREATE TABLE Node
	(Node_ID 	TEXT,
	Node_Type	TEXT,
	MAC_Address	TEXT,
	SW_Version	TEXT,
	Node_Location	TEXT,
	Node_Status	TEXT);''')
print ("  -> Node Table created successfully")

conn.execute('''CREATE TABLE Sensor_Data
	(Node_ID	TEXT,
	Date_Time	INT,
	Temperature	REAL,
	Humidity	REAL,
	Pressure	REAL,
	Analog_1	INT,
	Digital_1	INT,
	Digital_2	INT,
	Sequence        INT);''')
print ("  -> Data Table created successfully")

conn.execute('''CREATE TABLE Alert
	(Date_Time	INT,
	Alert_Source	TEXT,
	Alert_Message	TEXT,
	Alert_Sent	TEXT,
	Alert_Status	TEXT);''')
print ("  -> Alert Table created successfully")

conn.execute('''CREATE TABLE User
	(User_Name	TEXT,
	Email_Address	TEXT,
	Mobile_Number	TEXT,
	User_Status	TEXT);''')
print ("  -> User Table created successfully")

print ("Seeding the Database")
print ("  -> Node Table is seeded by the sensor data feed")
print ("  -> Sensor_Data Table is seeded by the sensor data feed")
print ("  -> Alert Table is seeded by the Data Update alert logic")

conn.execute("INSERT INTO User (User_Name, Email_Address, Mobile_Number, User_Status) \
	VALUES ('Geofrey Cardoza', 'geof.cardoza@gmail.com', '416-570-9354', 'Enabled')");
conn.execute("INSERT INTO User (User_Name, Email_Address, Mobile_Number, User_Status) \
	VALUES ('Lisa Cardoza', 'lisa.a.cardoza@gmail.com', '416-605-9354', 'Disabled')");

print ("  -> User Table seeded successfully")

conn.commit()

print ("Data has been committed to the database")
conn.close()

