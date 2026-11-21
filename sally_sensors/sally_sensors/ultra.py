#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import time


class SerialUltra(Node):
    def __init__(self):
        super().__init__("ultra")
        self.ultra_pub =  self.create_publisher( 
            Float32,
            '/sally/dist',
            10
        )

        self.rh_ultra_sub = self.create_subscription(
            Float32, 
            '/sally/rh_dist', 
            self.distancia(), 
            10
            )
            
        

    def distancia(self, pulse_duration):

        duration = Float32()
        duration = pulse_duration.data

        # Pasar velocidad del sonido a distancia -- m a cm (34300) y dividido en 2
        distance = duration * 17150

        self.ultra_pub.publish(distance)

def main(args=None):
    rclpy.init(args=args)
    node = SerialUltra()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()



