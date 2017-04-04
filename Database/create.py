#!/usr/bin/python3

import sqlite3

conn = sqlite3.connect('biot.db')
print ("Opened BIOT database successfully")

print("Creating Node Table")
conn.execute('''CREATE TABLE IF NOT EXISTS Node
	(Node_ID 	    TEXT,
	Node_Type	    TEXT,
	MAC_Address	    TEXT,
	SW_Version	    TEXT,
	Node_Status	    TEXT,
	Node_Location	TEXT);''')
print ("  -> Node Table created successfully")
conn.execute("INSERT INTO Node (Node_ID, MAC_Address, Node_Status, Node_Location) \
	VALUES ('RIOT2-5c:cf:7f:87:5b:a6', '5c:cf:7f:87:5b:a6', 'Inactive', '1. Main Floor')");
conn.execute("INSERT INTO Node (Node_ID, MAC_Address, Node_Status, Node_Location) \
	VALUES ('RIOT2-5c:cf:7f:15:61:f5', '5c:cf:7f:15:61:f5', 'Inactive', '2. Upstairs')");
conn.execute("INSERT INTO Node (Node_ID, MAC_Address, Node_Status, Node_Location) \
	VALUES ('RIOT2-5c:cf:7f:15:16:e4', '5c:cf:7f:15:16:e4', 'Inactive', '3. Basement')");
conn.execute("INSERT INTO Node (Node_ID, MAC_Address, Node_Status, Node_Location) \
	VALUES ('RIOT2-5c:cf:7f:c6:d2:f0', '5c:cf:7f:c6:d2:f0', 'Inactive', '4. Attic')");
conn.execute("INSERT INTO Node (Node_ID, MAC_Address, Node_Status, Node_Location) \
	VALUES ('RIOT2-5c:cf:7f:87:5d:7f', '5c:cf:7f:87:5d:7f', 'Inactive', '5. Outside')");
conn.execute("INSERT INTO Node (Node_ID, MAC_Address, Node_Status, Node_Location) \
	VALUES ('RIOT2-5c:cf:7f:87:5d:xx', '5c:cf:7f:87:5d:7f', 'Inactive', '6. Laundry Rm')");
conn.execute("INSERT INTO Node (Node_ID, MAC_Address, Node_Status, Node_Location) \
	VALUES ('RIOT2-5c:cf:7f:0d:d8:b3', '5c:cf:7f:15:16:e4', 'Inactive', '7. Water Mech Rm')");
conn.execute("INSERT INTO Node (Node_ID, MAC_Address, Node_Status, Node_Location) \
	VALUES ('RIOT3-5c:cf:7f:00:72:6e', '5c:cf:7f:00:72:6e', 'Inactive', '8. Irrigation System')");
print ("  -> Node Table seeded successfully")

print ("Creating Sensor_Data Table")
conn.execute('''CREATE TABLE IF NOT EXISTS Sensor_Data
	(Node_ID	    TEXT,
	Date_Time	    INT,
	Temperature	    REAL,
	Humidity	    REAL,
	Pressure	    REAL,
	Sequence        INT,
	Analog  	    INT,
	Alarm   	    INT,
	Digital_1	    INT);''')
print ("  -> Sensor_Data Table created successfully")
print ("  -> Sensor_Data Table is seeded by the sensor data feed")

print ("Creating User Table")
conn.execute('''CREATE TABLE IF NOT EXISTS User
	(User_Name	    TEXT,
	Email_Address	TEXT,
	Mobile_Number	TEXT,
	User_Status	    TEXT);''')
print ("  -> User Table created successfully")
conn.execute("INSERT INTO User (User_Name, Email_Address, Mobile_Number, User_Status) \
	VALUES ('Geofrey Cardoza', 'geof.cardoza@gmail.com', '416-570-9354', 'Enabled')");
conn.execute("INSERT INTO User (User_Name, Email_Address, Mobile_Number, User_Status) \
	VALUES ('Lisa Cardoza', 'lisa.a.cardoza@gmail.com', '416-605-9354', 'Disabled')");
conn.execute("INSERT INTO User (User_Name, Email_Address, Mobile_Number, User_Status) \
	VALUES ('BioT RioT', 'biot.riot@gmail.com', '416-605-9354', 'Enabled')");
print ("  -> User Table seeded successfully")

print ("Creating Alert_Status Table")
conn.execute('''CREATE TABLE IF NOT EXISTS Alert_Status
	(Date_Time  INT,
	Node_Location   TEXT,
    Alert_ID    TEXT,
	Alert_Message   TEXT,
	Alert_Status	TEXT);''')
print ("  -> Alert_Status Table created successfully")
print ("  -> Alert_Status Table is seeded by the Alert Update logic")

print ("Creating Alert_Messages Table")
conn.execute('''CREATE TABLE IF NOT EXISTS Alert_Messages
	(Alert_ID 	    TEXT,
	Alert_Message	TEXT);''')
print ("  -> Alert_Messages Table created successfully")
conn.execute("INSERT INTO Alert_Messages (Alert_ID, Alert_Message) \
    VALUES ('TemperatureLow', 'The Temperature has dropped below ')");
conn.execute("INSERT INTO Alert_Messages (Alert_ID, Alert_Message) \
    VALUES ('TemperatureHigh', 'The Temperature has rissen above ')");
conn.execute("INSERT INTO Alert_Messages (Alert_ID, Alert_Message) \
    VALUES ('HumidityLow', 'The Humidity has dropped below ')");
conn.execute("INSERT INTO Alert_Messages (Alert_ID, Alert_Message) \
    VALUES ('HumidityHigh', 'The Humidity has rissen above ')");
conn.execute("INSERT INTO Alert_Messages (Alert_ID, Alert_Message) \
    VALUES ('PressureLow', 'The Pressure has dropped below ')");
conn.execute("INSERT INTO Alert_Messages (Alert_ID, Alert_Message) \
    VALUES ('PressureHigh', 'The Pressure has rissen above ')");
conn.execute("INSERT INTO Alert_Messages (Alert_ID, Alert_Message) \
    VALUES ('WaterLeak', '***** WATER LEAK DETECTED - ACT NOW *****')");
print ("  -> Alert_Messages Table seeded successfully")

print ("Creating Alert_Rules Table");
conn.execute('''CREATE TABLE IF NOT EXISTS Alert_Rules
	( Node_ID 	        TEXT,
    Low_Temperature   REAL,
    High_Temperature  REAL,
    Low_Humidity      REAL,
    High_Humidity     REAL,
    Low_Pressure      REAL,
    High_Pressure     REAL,
    Alarm_Value       REAL,
    Update_Delay      REAL);''')
print ("  -> Alert_Rules Table created successfully")
conn.execute("INSERT INTO Alert_Rules (Node_ID, Low_Temperature, High_Temperature, Low_Humidity, High_Humidity, Low_Pressure, High_Pressure, Alarm_Value, Update_Delay) \
	VALUES ('RIOT2-5c:cf:7f:c6:ad:5c', 15, 30, 20, 90, 100, 103, 1, 3600)");
conn.execute("INSERT INTO Alert_Rules (Node_ID, Low_Temperature, High_Temperature, Low_Humidity, High_Humidity, Low_Pressure, High_Pressure, Alarm_Value, Update_Delay) \
	VALUES ('RIOT2-5c:cf:7f:00:72:6e', 15, 30, 20, 90, 100, 103, 1, 3600)");
conn.execute("INSERT INTO Alert_Rules (Node_ID, Low_Temperature, High_Temperature, Low_Humidity, High_Humidity, Low_Pressure, High_Pressure, Alarm_Value, Update_Delay) \
	VALUES ('RIOT2-5c:cf:7f:0d:d8:b3', 15, 30, 20, 90, 100, 103, 1, 3600)");
conn.execute("INSERT INTO Alert_Rules (Node_ID, Low_Temperature, High_Temperature, Low_Humidity, High_Humidity, Low_Pressure, High_Pressure, Alarm_Value, Update_Delay) \
	VALUES ('RIOT2-5c:cf:7f:c6:d2:f0', 15, 30, 20, 90, 100, 103, 1, 3600)");
conn.execute("INSERT INTO Alert_Rules (Node_ID, Low_Temperature, High_Temperature, Low_Humidity, High_Humidity, Low_Pressure, High_Pressure, Alarm_Value, Update_Delay) \
	VALUES ('RIOT2-5c:cf:7f:c6:aa:f4',  5, 30, 20, 90, 100, 103, 1, 3600)");
print ("  -> Alert_Rules Table seeded successfully")

conn.execute('''CREATE TABLE IF NOT EXISTS Zone
	( Zone_ID             INT,
    Node_ID             TEXT,
	  Zone_Location       TEXT,
    Irrigation_Type     TEXT,
	  Scheduled_OnTime    INT,
    Current_Zone_Status TEXT,
    Last_OnTime         INT,
    Last_Date_Time_On   INT,
    Last_Date_Time_Off  INT);''')
print ("  -> Zone Table created successfully")
conn.execute("INSERT INTO Zone (Zone_ID, Zone_Location, Irrigation_Type, Scheduled_OnTime) \
	VALUES (1, 'Front Lawn - East Side', 'Sprayer', 1800)");
conn.execute("INSERT INTO Zone (Zone_ID, Zone_Location, Irrigation_Type, Scheduled_OnTime) \
	VALUES (2, 'Front Lawn - Centre Area', 'Sprayer', 1800)");
conn.execute("INSERT INTO Zone (Zone_ID, Zone_Location, Irrigation_Type, Scheduled_OnTime) \
	VALUES (3, 'Front Lawn - West Side', 'Sprayer', 1800)");
conn.execute("INSERT INTO Zone (Zone_ID, Zone_Location, Irrigation_Type, Scheduled_OnTime) \
	VALUES (4, 'Vegetable Garder and East Entrance', 'Soaker', 3600)");
conn.execute("INSERT INTO Zone (Zone_ID, Zone_Location, Irrigation_Type, Scheduled_OnTime) \
	VALUES (5, 'Front Sitting Area and West Entrance', 'Soaker', 3600)");
conn.execute("INSERT INTO Zone (Zone_ID, Zone_Location, Irrigation_Type, Scheduled_OnTime) \
	VALUES (6, 'Kitchen Sitting Area and Front Office', 'Soaker', 3600)");
conn.execute("INSERT INTO Zone (Zone_ID, Zone_Location, Irrigation_Type, Scheduled_OnTime) \
	VALUES (7, 'Future TBD', 'Drip', 0)");
conn.execute("INSERT INTO Zone (Zone_ID, Zone_Location, Irrigation_Type, Scheduled_OnTime) \
	VALUES (8, 'Future TBD', 'Drip', 0)");
print ("  -> Zone Table seeded successfully")

conn.execute('''CREATE TABLE IF NOT EXISTS Zone_Status
	( Zone_ID         INT,
    Node_ID         TEXT,
    Date_Time       INT,
    Zone_Status     TEXT,
    Zone_Ontime     INT);''')
print ("  -> Zone_Status Table created successfully")
print ("  -> Zone_Status Table seeded by RioT3 Status Updates")

conn.commit()

print ("Data has been committed to the database")
conn.close()







