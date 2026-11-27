#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sally_msgs.msg import CarMovement


class SallyMovement(Node):

    def __init__(self):
        super().__init__("sally_movement")

        self.velocity = CarMovement()
        self.current_movement = "STOP"
        self.speed = 0.2 

        self.velocity_publisher = self.create_publisher(
            CarMovement,
            "/sally/cmd_vel",
            10
        )

        self.decision_subscription = self.create_subscription(
            CarMovement,
            "/sally/decision",
            self.decision_callback,
            10
        )

    def decision_callback(self, message):

        decision = message.rute
        self.velocity.direction = message.direction

        if decision == "FORWARD":
            self.move_forward()

        elif decision == "BACKWARD":
            self.move_backward()
        else:
            self.stop()


    def move_forward(self):

        self.velocity.speed = self.speed
        self.velocity.rute = "FORWARD"

        self.velocity_publisher.publish(self.velocity)
        self.current_movement = "FORWARD"
        
        self.get_logger().info("Sally moving forward!")

    def move_backward(self):

        self.velocity.speed = self.speed
        self.velocity.rute = "BACKWARD"
        self.velocity_publisher.publish(self.velocity)
        self.current_movement = "BACKWARD"

        self.get_logger().info("Sally moving backward!")

    def stop(self):

        self.velocity.speed = 0
        self.velocity.rute = "STOP"
        self.velocity_publisher.publish(self.velocity)
        self.current_movement = "STOP"

        self.get_logger().info("Sally stopped!") 


def main (args=None):
    rclpy.init(args=args)
    node = SallyMovement()
    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        node.stop()

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()