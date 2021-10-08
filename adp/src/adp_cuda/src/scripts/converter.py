#!/usr/bin/env python
# -*- coding: utf-8 -*-


# This import is for ROS integration
import rospy
from sensor_msgs.msg import Image


def cb(msg):
    pub = rospy.Publisher('/camera/image', Image, queue_size = 1)
    conv_image = Image()
    conv_image = msg
    #print(conv_image)
    pub.publish(conv_image)

def main():
    rospy.init_node('image_conv', anonymous = True)
    rospy.Subscriber('/Sensor/RealSense435i/color/image_raw', Image, cb)
    rate = rospy.Rate(10)
    rospy.spin()
    rate.sleep

if __name__ == '__main__':
    main()

