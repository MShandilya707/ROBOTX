#!/usr/bin/env python3

import rospy
from std_msgs.msg import Int32

class ModeUAVSimulator:
    def __init__(self):
        rospy.init_node('mode_uav_simulator', anonymous=True)
        
        # Publishers for MODE and UAV topics
        self.mode_pub = rospy.Publisher('MODE', Int32, queue_size=10)
        self.uav_pub = rospy.Publisher('UAV', Int32, queue_size=10)
        
        # Publish at 1 Hz
        self.rate = rospy.Rate(1)
        self.system_mode = 2  # Default mode for testing
        self.uav_status = 1   # Default UAV status for testing

    def publish_simulated_data(self):
        while not rospy.is_shutdown():
            # Publishing simulated data
            self.mode_pub.publish(self.system_mode)
            self.uav_pub.publish(self.uav_status)
            
            rospy.loginfo(f"Simulated MODE: {self.system_mode}")
            rospy.loginfo(f"Simulated UAV: {self.uav_status}")
            
            # Change values for testing if desired
            # (e.g., alternate between different values to simulate changing states)
            self.system_mode = 3 if self.system_mode == 2 else 2
            self.uav_status = 0 if self.uav_status == 1 else 1
            
            self.rate.sleep()

if __name__ == '__main__':
    try:
        simulator = ModeUAVSimulator()
        simulator.publish_simulated_data()
    except rospy.ROSInterruptException:
        pass
