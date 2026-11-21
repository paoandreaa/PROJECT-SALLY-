#!/usr/bin/env python3

import sys
import termios
import tty
import curses

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

class manual_driving(Node):

    def __init__(self):
        super().__init__("drive_manual")

        self.manual_directions = self.create_publisher(
            Float32,
            "/sally/cmd_movement",
            10
        )

    def read_key(self):
        key = self.getch()


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