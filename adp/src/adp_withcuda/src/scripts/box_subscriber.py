#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from darknet_ros_msgs.msg import BoundingBoxes,BoundingBox
pub = rospy.Publisher('/darknet_ros/bounding_box', BoundingBox, queue_size=10)

def callback(data):
    for i in data.bounding_boxes:
        pub.publish(i)
        print(i)
"""i(BoundingBox) has following data
float64 probability
int64 xmin
int64 ymin
int64 xmax
int64 ymax
int16 id
string Class"""

def listener():
    rospy.init_node('pub_box')
    rospy.Subscriber("/darknet_ros/bounding_boxes", BoundingBoxes, callback)
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()
        
if __name__ == '__main__':
    listener()