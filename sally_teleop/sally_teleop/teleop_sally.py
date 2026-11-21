#!/usr/bin/env python3

import sys
import termios
import tty

import rclpy
from rclpy.node import Node

from sally_msgs.msg import ServoHead


class SallyTeleop(Node):

    def __init__(self):
        super().__init__("sally_teleop")

        self.angle_publisher = self.create_publisher(
            ServoHead,
            "/sally/servo_command",
            10
        )

        # Agulos iniciales
        self.angle_1 = 90.0
        self.angle_2 = 90.0

        # Incremento de movimiento
        self.step = 5.0

        self.get_logger().info(
            "Teleoperation started! "
            "A/D: Servo 1 | J/L: Servo 2 | Q: Exit"
        )

    def read_key(self):

        key = sys.stdin.read(1).lower()

        if key == "q":
            return False

        elif key == "a":
            self.angle_1 -= self.step

        elif key == "d":
            self.angle_1 += self.step

        elif key == "j":
            self.angle_2 -= self.step

        elif key == "l":
            self.angle_2 += self.step

        else:
            return True

        # Limitar los ángulos de ambos servos
        self.angle_1 = max(0.0, min(180.0, self.angle_1))
        self.angle_2 = max(0.0, min(180.0, self.angle_2))

        # Crear mensaje
        message = ServoHead()

        ServoHead.servo1 = self.angle_1
        ServoHead.servo2 = self.angle_2

        # Publicar ambos ángulos
        self.angle_publisher.publish(message)

        print(
            f"\rServo 1: {self.angle_1:.1f}° | "
            f"Servo 2: {self.angle_2:.1f}°",
            end="",
        )

        return True


def main(args=None):

    rclpy.init(args=args)

    node = SallyTeleop()

    terminal = sys.stdin.fileno()
    original_settings = termios.tcgetattr(terminal)

    try:

        tty.setraw(terminal)

        while rclpy.ok():

            if not node.read_key():
                break

    finally:

        # Restaurar el terminal
        termios.tcsetattr(
            terminal,
            termios.TCSADRAIN,
            original_settings
        )

        # Regresar a una nueva línea
        print("\n")

        node.get_logger().info("Teleoperation finished.")

        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()