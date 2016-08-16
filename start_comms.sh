#!/bin/bash

hciconfig
read
hcitool scan
read
sudo rfcomm bind /dev/rfcomm1 20:16:01:25:66:84 1
sudo rfcomm bind /dev/rfcomm8 20:16:01:25:69:75 1
read
rfcomm
