#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import rospy
import rclpy
from rclpy.node import Node
import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image


img = Image()
start_ok = False
def callback_img(msg):
    global img, start_ok
    img = msg
    start_ok = True


def main():
    global img, start_ok
    rclpy.init()
    nd = Node("catch_img")
    sub = nd.create_subscription(Image, "/camera/camera/color/image_raw", callback_img, 1) # /camera/camera/color/image_raw /camera/camera/depth/color/points
    while rclpy.ok():
        rclpy.spin_once(nd, timeout_sec=0.1)
        if start_ok:
            break      # 画像がコールバックされたら抜け出す
    
    if start_ok:
        print("撮影まで...\n3")
        rclpy.spin_once(nd, timeout_sec=1.0)
        print("2")
        rclpy.spin_once(nd, timeout_sec=1.0)
        print("1")
        rclpy.spin_once(nd, timeout_sec=1.0)

        bridge = CvBridge()
        image = bridge.imgmsg_to_cv2(img)
        if img.encoding == "rgb8":
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        cv2.imwrite('result.png', image)
        # rclpy.spin(nd)


if __name__ == '__main__':
    main()