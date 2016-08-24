#!/usr/bin/python3

import sqlite3

conn = sqlite3.connect('BIOT_Base.db')
print "Opened BIOT database successfully";

conn.execute("INSERT INTO Node (Node_ID, Node_Type, SW_Version, Serial_Port, MAC_Address, Node_Location, Node_Status) \
	VALUES (1, 'RIOT1', '0.7', '/dev/rfcomm1', '20:16:01:25:66:84', 'Main Floor', 'Active')");
conn.execute("INSERT INTO Node (Node_ID, Node_Type, SW_Version, Serial_Port, MAC_Address, Node_Location, Node_Status) \
	VALUES (2, 'RIOT1', '0.7', '/dev/rfcomm2', '20:16:01:25:69:75', 'Second Floor', 'Inactive')");
conn.execute("INSERT INTO Node (Node_ID, Node_Type, SW_Version, Serial_Port, MAC_Address, Node_Location, Node_Status) \
	VALUES (3, 'RIOT1', 'v0.7', '/dev/rfcomm3', '0',  'Basement', 'Inactive')");
conn.execute("INSERT INTO Node (Node_ID, Node_Type, SW_Version, Serial_Port, MAC_Address, Node_Location, Node_Status) \
	VALUES (4, 'RIOT1', 'v0.7', '/dev/rfcomm4', '0',  'Attic', 'Inactive')");
conn.execute("INSERT INTO Node (Node_ID, Node_Type, SW_Version, Serial_Port, MAC_Address, Node_Location, Node_Status) \
	VALUES (5, 'RIOT1', 'v0.7', '/dev/rfcomm5', '0',  'Outside', 'Inactive')");
conn.execute("INSERT INTO Node (Node_ID, Node_Type, SW_Version, Serial_Port, MAC_Address, Node_Location, Node_Status) \
	VALUES (6, 'RIOT1', 'v0.7', '/dev/rfcomm6', '0',  'TBD', 'Inactive')");
conn.execute("INSERT INTO Node (Node_ID, Node_Type, SW_Version, Serial_Port, MAC_Address, Node_Location, Node_Status) \
	VALUES (7, 'RIOT1', 'v0.7', '/dev/rfcomm7', '0',  'TBD', 'Inactive')");
conn.execute("INSERT INTO Node (Node_ID, Node_Type, SW_Version, Serial_Port, MAC_Address, Node_Location, Node_Status) \
	VALUES (8, 'RIOT1', 'v0.7', '/dev/rfcomm8', '0',  'Test', 'Active')");
conn.commit()
print "Node Table seeded successfully";

# conn.execute("INSERT INTO Sensor_Data (Node_ID, Date_Stamp, Time_Stamp, DHT22_Temperature, DHT22_Humidity, BMP180_Temperature, BMP180_Pressure, Moisture_1, Moisture_2, Moisture_3) \
#	VALUES (1, '20160627', '21:08:30', 30.1, 45.1, 30.2, 101.6, 20.1, 55.6, 98.4)");
#conn.execute("INSERT INTO Sensor_Data (Node_ID, Date_Stamp, Time_Stamp, DHT22_Temperature, DHT22_Humidity, BMP180_Temperature, BMP180_Pressure, Moisture_1, Moisture_2, Moisture_3) \
#	VALUES (1, '20160627', '21:08:32', 29.2, 48.2, 29.6, 101.2, 20.2, 55.3, 98.5)");
#conn.execute("INSERT INTO Sensor_Data (Node_ID, Date_Stamp, Time_Stamp, DHT22_Temperature, DHT22_Humidity, BMP180_Temperature, BMP180_Pressure, Moisture_1, Moisture_2, Moisture_3) \
#	VALUES (1, '20160627', '21:08:34', 28.1, 46.2, 28.2, 101.3, 20.3, 55.1, 98.6)");
#conn.commit()
#print "Data Table seeded successfully";

conn.execute("INSERT INTO Alert (Date_Stamp, Time_Stamp, Alert_Source, Alert_Message, Alert_Sent, Alert_Status) \
	VALUES ('2016-06-27', '18:23:34', 'Second Floor Water Leak', 'There is a flood', 'Yes', 'Active')");
conn.commit()
print "Alert Table seeded successfully";

conn.execute("INSERT INTO User (User_Name, Email_Address, Mobile_Number, User_Status) \
	VALUES ('Geofrey Cardoza', 'geof.cardoza@gmail.com', '416-570-9354', 'Enabled')");
conn.execute("INSERT INTO User (User_Name, Email_Address, Mobile_Number, User_Status) \
	VALUES ('Lisa Cardoza', 'lisa.a.cardoza@gmail.com', '416-605-9354', 'Disabled')");
conn.commit()
print "User Table seeded successfully";

print "Data has been committed to the database";

conn.close()

