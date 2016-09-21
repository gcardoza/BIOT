#!/bin/bash

mosquitto_sub -t "/RioT/SensorData" | ts "%b %d %H:%M:%S," | tee -a ./LogFiles/sensordata.log
