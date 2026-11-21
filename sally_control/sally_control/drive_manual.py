#!/usr/bin/env python3

import time
import curses

import rclpy
from rclpy.node import Node
from std_msgs.msg import Twist

class manual_driving(Node):

    def __init__(self):
        super().__init__("drive_manual")

        self.manual_directions = self.create_publisher(
            Twist,
            "/sally/cmd_movement",
            10
        )

        self.speed = 0.2 

        self.timer = self.create_timer(0.1, self.read_key)

    def read_key(self):
        key = self.getch()
        velocity = Twist()

        if(key == curses.KEY_UP):
            velocity.linear.x = self.speed
            velocity.angular.x = 1.0
            self.velocity_publisher.publish(velocity)
        elif(key == curses.KEY_DOWN):
            velocity.linear.x = self.speed
            velocity.angular.x = -1.0
            self.velocity_publisher.publish(velocity)
        else:
            velocity.linear.x = self.speed
            velocity.angular.x = 0
            self.velocity_publisher.publish(velocity)


def main(args=None):
    rclpy.init(args=args)
    node = manual_driving()
    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()