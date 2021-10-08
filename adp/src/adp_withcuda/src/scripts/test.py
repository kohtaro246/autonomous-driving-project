#!/usr/bin/env python
#general lib
import os
import threading
​
import rospy
import math
import actionlib
import cv2
#import necessary stuff for YOLO
from sensor_msgs.msg import Image,CameraInfo
from cv3_bridge import CvBridge, CvBridgeError
import numpy as np
from darknet_ros_msgs.msg import BoundingBoxes, BoundingBox

#END import necessary stuff for YOLO
​
#boxes=BoundingBox()
person = BoundingBox() 
def cb(darknet_bboxs):
    bboxs = darknet_bboxs.bounding_boxes
    #print(bboxs)
    global person
    if len(bboxs) != 0 :
        for i, bb in enumerate(bboxs) :
            if bboxs[i].Class == 'person' and bboxs[i].probability >= 0.4:
                person = bboxs[i]        
                
                
​
​
if __name__ == '__main__':
    try:
        rospy.init_node('client')
        rospy.Subscriber('/darknet_ros/bounding_boxes', BoundingBoxes, cb)
        
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            
            rate.sleep()
​
    except rospy.ROSInterruptException: pass