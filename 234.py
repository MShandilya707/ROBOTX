import socket
import sys
from datetime import datetime
import pytz
import random
import time
import os
import json
import threading
from dronekit import connect
from collections.abc import MutableMapping

# Initialize GPS variables for USV and UAV
usv_lat = 27.37416  # Default USV latitude
usv_long = 82.45264  # Default USV longitude
uav_lat = 27.37416  # Default UAV latitude
uav_long = 82.45264  # Default UAV longitude

# Initialize mode for UAV (2 = autonomous mode)
autonomous_mode = 2

EASTERN_TIME = pytz.timezone('US/Eastern')
PACIFIC_TIME = pytz.timezone("US/Pacific")

def get_date():
    current_time = datetime.now(EASTERN_TIME)
    est_date = current_time.strftime("%d%m%y")
    return est_date

def get_time():
    current_time = datetime.now(EASTERN_TIME)
    est_time = current_time.strftime("%H%M%S")
    return est_time

def attach_checksum(nmea_sentence):
    """Calculates and attaches a checksum to an NMEA sentence."""
    sentence = nmea_sentence.strip("$!*")
    checksum = 0
    for char in sentence:
        checksum ^= ord(char)
    return f"${sentence}*{checksum:02X}"

entity = 'NTCH'

# Connect to the Pixhawk devices for USV and UAV
try:
    usv_vehicle = connect('COM9', baud=57600)
except Exception as e:
    print(f"Failed to connect to Pixhawk devices: {e}")
    sys.exit(1)

# Define callback functions for GPS data
def usv_gps_callback(self, name, message):
    global usv_lat, usv_long
    try:
        usv_lat = abs(message.lat / 1e7)  # Convert to decimal degrees
        usv_long = abs(message.lon / 1e7)
        print(usv_lat, usv_long)
    except:
        pass

# Placeholder function to check UAV mode (to be implemented later)
def check_uav_mode():
    # Future implementation for determining the UAV mode
    pass

# Listen to GPS_RAW_INT messages for both USV and UAV
usv_vehicle.add_message_listener('GPS_RAW_INT', usv_gps_callback)




with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect(('robot.server', 12345))

    counter = 0
    lot = True

    for x in range(100000000):
        counter+=1
        try:
            usv_data = f"RXHRB,{get_date()},{get_time()},{usv_lat},N,{usv_long},W,{entity},2,1"
            usv_nmea_hrb_msg = attach_checksum(usv_data)

            usv_data_undocked = f"RXHRB,{get_date()},{get_time()},{usv_lat},N,{usv_long},W,{entity},2,2"
            usv_nmea_hrb_undocked = attach_checksum(usv_data_undocked)
        except:
            usv_data = f"RXHRB,{get_date()},{get_time()},27.37416,N,82.45264,W,{entity},2,1"
            usv_nmea_hrb_msg = attach_checksum(usv_data)

            usv_data_undocked = f"RXHRB,{get_date()},{get_time()},27.37416,N,82.45264,W,{entity},2,2"
            usv_nmea_hrb_undocked = attach_checksum(usv_data_undocked)

        usv_gate = f"RXGAT,{get_date()},{get_time()},{entity},3,3"
        usv_nmea_hrb_msg2 = attach_checksum(usv_gate)

        usv_follow_inprog = f"RXPTH,{get_date()},{get_time()},{entity},R,1"
        usv_nmea_hrb_msg_inprog = attach_checksum(usv_follow_inprog)

        usv_follow_complete = f"RXPTH,{get_date()},{get_time()},{entity},R,2"
        usv_nmea_hrb_msg_complete = attach_checksum(usv_follow_complete)

        usv_scan = f"RXCOD,{get_date()},{get_time()},{entity},RBR"
        usv_nmea_hrb_msg_scan = attach_checksum(usv_scan)

        sock.sendall(bytes(usv_nmea_hrb_msg + "\n", "utf-8"))
        print(f"Sent USV Heartbeat message: {usv_nmea_hrb_msg}")


        if 40 >= counter:

            sock.sendall(bytes(usv_nmea_hrb_msg2 + "\n", "utf-8"))
            print(f"Sent USV Heartbeat message: {usv_nmea_hrb_msg2}")
            print()

        elif 60 >= counter:
            sock.sendall(bytes(usv_nmea_hrb_msg_scan + "\n", "utf-8"))
            print(f"Sent USV Heartbeat message: {usv_nmea_hrb_msg_scan}")
            print()

        elif 75 >= counter:
            sock.sendall(bytes(usv_nmea_hrb_msg_inprog + "\n", "utf-8"))
            print(f"Sent USV Heartbeat message: {usv_nmea_hrb_msg_inprog}")
            print()

        elif 90 >= counter:
            sock.sendall(bytes(usv_nmea_hrb_msg_inprog + "\n", "utf-8"))
            print(f"Sent USV Heartbeat message: {usv_nmea_hrb_msg_inprog}")
            print()


        elif 120 >= counter:

            sock.sendall(bytes(usv_nmea_hrb_msg_inprog + "\n", "utf-8"))
            print(f"Sent USV Heartbeat message: {usv_nmea_hrb_msg_inprog}")
            print()


        else:

            if lot == True:
                sock.sendall(bytes(usv_nmea_hrb_msg_complete + "\n", "utf-8"))
                print(f"Sent USV Heartbeat message: {usv_nmea_hrb_msg_complete}")
                lot = False
            elif lot == False:
                pass


            sock.sendall(bytes(usv_nmea_hrb_msg2 + "\n", "utf-8"))
            print(f"Sent USV Heartbeat message: {usv_nmea_hrb_msg2}")
            print()
        time.sleep(1)

# Close vehicle connections when the loop ends
usv_vehicle.close()
