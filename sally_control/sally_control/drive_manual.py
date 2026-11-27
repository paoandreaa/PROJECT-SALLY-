#!/usr/bin/env python3

import time
from pynput import keyboard

import rclpy
from rclpy.node import Node
from sally_msgs.msg import CarMovement

class manual_driving(Node):

    def __init__(self):
        super().__init__("drive_manual")

        self.manual_directions = self.create_publisher(
            CarMovement,
            "/sally/cmd_vel",
            10
        )

        # Estado de las teclas
        self.forward = False
        self.backward = False
        self.right = False
        self.left = False

        # Listener del teclado
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )

        self.speed = 0.2 

        self.listener.start()

        
        self.timer = self.create_timer(0.1, self.read_key)

    def on_press(self, key):
        if key == keyboard.Key.up:
            self.forward = True

        elif key == keyboard.Key.down:
            self.backward = True

        elif key == keyboard.Key.right:
            self.right = True

        elif key == keyboard.Key.left:
            self.left = True

    def on_release(self, key):

        if key == keyboard.Key.up:
            self.forward = False

        elif key == keyboard.Key.down:
            self.backward = False

        elif key == keyboard.Key.right:
            self.right = False

        elif key == keyboard.Key.left:
            self.left = False
    
    def read_key(self):
        velocity = CarMovement()
        velocity.rute = "STOP"
        velocity.direction = "STRAIGHT"
        velocity.speed = self.speed

        if(self.forward):
            velocity.rute = "FORWARD"
        elif(self.backward):
            velocity.rute = "BACKWARD"
        else:
            velocity.rute = "STOP"

        if self.right:
            velocity.direction = "RIGHT"
        elif self.left:
            velocity.direction = "LEFT"
        else:
            velocity.direction = "STRAIGHT"
        
        self.manual_directions.publish(velocity)

    def destroy_node(self):
        velocity = CarMovement()
        velocity.rute = "STOP"
        velocity.direction = "STRAIGHT"
        velocity.speed = 0.0

        self.manual_directions.publish(velocity)

        self.listener.stop()

        super().destroy_node()


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