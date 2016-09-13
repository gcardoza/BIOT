#!/bin/bash

mosquitto_sub -t "/RIOT2/SensorData" | ts "%b %d %H:%M:%S," | tee -a ./LogFiles/sensordata.log
