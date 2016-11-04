#!/bin/bash

mosquitto_sub -t "/RioT/Status" | ts "%b %d %H:%M:%S,"