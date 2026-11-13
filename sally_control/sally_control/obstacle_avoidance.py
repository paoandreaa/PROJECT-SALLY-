#!/usr/bin/env python3

import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String 


class SallyExploration(Node):

    def __init__(self):
        super().__init__("sally_exploration")

        self.head_publisher = self.create_publisher(
            Float32, 
            "/sally/servo_command", 
            10
        )

        self.decision_publisher = self.create_publisher(
            String,
            "/sally/decision",
            10
        )

        self.distance_subscriber = self.create_subscription(
            Float32,
            "dist",
            self.distance_callback,
            10
        )

        self.directions = [90.0, 45.0, 135.0]
        self.index = 0

        self.distance = None
        self.blocked_until = [0.0, 0.0, 0.0]

        self.waiting = False
        self.move_time = 0.0

        self.timer = self.create_timer(
            0.1, 
            self.exploration_callback
        )

    def distance_callback(self, message):
        self.distance = message.data

    def exploration_callback(self):

        now = time.monotonic()

        # Si todavía estamos esperando que se mueva el servo
        if self.waiting:

            if now - self.move_time < 0.5:
                return

            # Esperar una medición del sensor
            if self.distance is None:
                return

            distance = self.distance
            self.distance = None
            self.waiting = False

            decision = String()

            # Comprobar si hay un obstáculo
            if distance > 0 and distance < 15.0:


                self.blocked_until[self.index] = now + 3.0


                decision.data = "BACKWARD"

                self.get_logger().info("Obstacle detected. Avoiding direction.")

            else: 
                decision.data = "FORWARD"

                self.get_logger().info("Path clear!")

            self.decision_publisher.publish(decision)
            self.index = (self.index + 1) % 3

        # Buscar la siguiente dirección disponible
        for _ in range(3):

            if now >= self.blocked_until[self.index]:

                angle = Float32()
                angle.data = self.directions[self.index]

                self.head_publisher.publish(angle)

                self.move_time = now
                self.waiting = True

                return

            self.index = (self.index + 1) % 3


def main(args=None):

    rclpy.init(args=args)
    node = SallyExploration()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
