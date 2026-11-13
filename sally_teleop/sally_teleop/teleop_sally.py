#!/usr/bin/env python3

import sys
import termios
import tty

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

# We understand what is a class? If is not, why we are used it? 
class SallyTeleop(Node):

    def __init__(self):
        super().__init__("sally_teleop")
        
        self.angle_publisher = self.create_publisher(
            Float32,
            "/sally/servo_command",
            10
        )

        # Could not be better, using ROS2 parameters ( used with config file inside "config" folder .yaml ), change the values here ? 
        self.angle = 90.0
        self.step = 5.0

        self.get_logger().info("Teleoperation started! Press: A: Left | D: Right | Q: Exit")

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

        # There is not another better way to saturate / limit the threshold of sending data inside an interval?
        self.angle = max(0.0, min(180.0, self.angle))

        message = Float32()
        message.data = float(self.angle)
        
        # Are you sure that we really do not need Timer here? The actuator is going to responds instantly?
        self.angle_publisher.publish(message)
        
        # \r asegura que vuelva al inicio de la línea y \n baja al siguiente renglón
        print(f"\r\n[INFO] [sally_teleop]: Angulo solicitado: {self.angle} grados", end="")

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
        
        
        # HERE: How can we do to ensure that the terminal prompt starts on a new line after exiting raw mode ? 
        # < the solution perhaps is wrote here >
        
        # Why not add another print notifying to the user that the teleop app is finalized?
        
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()