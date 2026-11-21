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
            self.distancia, 
            10
            )
            
        

    def distancia(self, pulse_duration):

        # Pasar velocidad del sonido a distancia -- m a cm (34300) y dividido en 2
 

        pub_dist = Float32()
        pub_dist .data= pulse_duration.data * 17150.0
        self.get_logger().info(f"¡Se logró perros hptas! {pub_dist.data}")
        
        self.ultra_pub.publish(pub_dist)

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



