
import sys
import termios
import tty

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class SallyTeleop(Node):

    def __init__(self):
        super().__init__("sally_teleop")

        self.angle_publisher = self.create_publisher(
            Float32,
            "/sally/servo_command",
            10
        )

        self.angle = 90.0
        self.step = 5.0

        self.get_logger().info(
            "Teleoperation started! Press: A: Left | D: Right | Q: Exit"
        )

    def read_key(self):
        key = sys.stdin.read(1).lower()

        if key == "q":
            return False
        if key == "a":
            self.angle -= self.step
        elif key == "d":
            self.angle += self.step
        else:
            return True

        self.angle = max(0.0, min(180.0, self.angle))

        message = Float32()
        message.data = float(self.angle)
        self.angle_publisher.publish(message)

        self.get_logger().info(
            f"Requested angle: {self.angle} degrees"
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
        termios.tcsetattr(
            terminal,
            termios.TCSADRAIN,
            original_settings
        )
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()