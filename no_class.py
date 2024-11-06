#!/usr/bin/env python3

import rospy
from std_msgs.msg import Int32
from sensor_msgs.msg import NavSatFix
from datetime import datetime
import uuid
import socket
import time
import pytz  # For timezone support

# Constants
TEAM_ID = "NTCH"  # Team ID constant
LATITUDE = 0.0
LONGITUDE = 0.0
NS_INDICATOR = 'N'
EW_INDICATOR = 'W'
SYSTEM_MODE = 2  # Default to Autonomous
UAV_STATUS = 1  # Default to Stowed
SOCKET = None


def gps_callback(msg):
    global LATITUDE, LONGITUDE, NS_INDICATOR, EW_INDICATOR
    LATITUDE = msg.latitude
    NS_INDICATOR = 'N' if msg.latitude >= 0 else 'S'
    LONGITUDE = msg.longitude
    EW_INDICATOR = 'E' if msg.longitude >= 0 else 'W'


def mode_callback(msg):
    global SYSTEM_MODE
    SYSTEM_MODE = msg.data


def uav_callback(msg):
    global UAV_STATUS
    UAV_STATUS = msg.data


def calculate_checksum(message):
    checksum = 0
    for char in message:
        checksum ^= ord(char)
    return f"{checksum:X}"  # Return as hexadecimal string


def create_heartbeat_message():
    unique_message_id = f"${uuid.uuid4().hex[:8].upper()}"

    # Get the current date and time in U.S. Eastern Standard Time (EST)
    est = pytz.timezone('US/Eastern')
    current_time = datetime.now(est)
    est_date = current_time.strftime("%d%m%y")
    est_time = current_time.strftime("%H%M%S")

    msg_without_checksum = f"RXHRB,{est_date},{est_time},{LATITUDE},{NS_INDICATOR}," \
                           f"{LONGITUDE},{EW_INDICATOR},{TEAM_ID},{SYSTEM_MODE},{UAV_STATUS}"

    checksum = calculate_checksum(msg_without_checksum)
    heartbeat_message = f"${msg_without_checksum}*{checksum}"

    return heartbeat_message


if __name__ == '__main__':
    rospy.Subscriber('/gps/gps_fix', NavSatFix, gps_callback)
    rospy.Subscriber('MODE', Int32, mode_callback)
    rospy.Subscriber('UAV', Int32, uav_callback)
    rospy.init_node('heartbeat_publisher', anonymous=True)
    server_hostname = 'robot.server'
    server_port = 12345
    rate = rospy.Rate(1)

    try:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((server_hostname, server_port))
            while not rospy.is_shutdown():
                heartbeat_message = create_heartbeat_message()
                try:
                    SOCKET.sendall(heartbeat_message.encode())
                    rospy.loginfo(f"Sent heartbeat message: {heartbeat_message}")
                except socket.error as e:
                    rospy.logerr(f"Failed to send heartbeat: {e}")
                    rospy.signal_shutdown("Socket send error")
                time.sleep(1)
            if sock:
                SOCKET.close()
                rospy.loginfo("Socket closed.")

    except rospy.ROSInterruptException:
        pass
