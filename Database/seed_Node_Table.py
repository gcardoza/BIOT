#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('BIOT_Base.db')
print "Opened BIOT database successfully";

conn.execute('''CREATE TABLE Node
	(Node_ID 	INT,
	Node_Type	TEXT,
	SW_Version	TEXT,
	Serial_Port	TEXT,
	MAC_Address	TEXT,
	Node_Location	TEXT,
	Node_Status	TEXT);''')
print "Node Table created successfully";

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

conn.close()

