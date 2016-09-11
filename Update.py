#!/usr/bin/python3

# Project:	BIOT Base Monitoring Station - Reads data from the RIOT devices via MQTT
# Author:	Geofrey Cardoza
# Company:	Excaliber Inc. (c)
# Baseline:	June 28th, 2016
# Revision:	August 15th, 2016  v1.0

import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

Broker = "192.168.0.37"

sub_topic = "/RIOT2/SensorData"    # receive messages on this topic

pub_topic = "/Config/RIOT2"               # send messages to this topic


# mqtt section

# when connecting to mqtt do this;

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(sub_topic)

# when receiving a mqtt message do this;

def on_message(client, userdata, msg):
    message = str(msg.payload)
    print(msg.topic+" "+message)
    publish_mqtt("got your message");

# to send a message

def publish_mqtt(sensor_data):
    mqttc = mqtt.Client("BIOT_Base")
    mqttc.connect(Broker, 1883)
    mqttc.publish(pub_topic, "this is the master speaking")
    #mqttc.loop(2) //timeout = 2s

def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(Broker, 1883, 60)
client.loo_forever()
