import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist 

class SallyMovement(Node):

    def __init__(self):
        super().__init__("sally_movement")

        self.current_movement = "STOP"
        self.speed = 0.2 

        self.velocity_publisher = self.create_publisher(
            Twist,
            "/sally/cmd_vel",
            10
        )

        self.decision_subscription = self.create_subscription(
            String,
            "/sally/decision",
            self.decision_callback,
            10
        )

    def decision_callback(self, message):

        decision = String()
        decision = message.data

        if decision == "FORWARD":
            self.move_forward()

        elif decision == "BACKWARD":
            self.move_backward()
        else:
            self.stop()

    def move_forward(self):

        velocity = Twist()
        velocity.linear.x = self.speed
        self.velocity_publisher.publish(velocity)
        self.current_movement = "FORWARD"
        
        self.get_logger().info("Sally moving forward!")

    def move_backward(self):

        velocity = Twist()
        velocity.linear.x = -self.speed
        self.velocity_publisher.publish(velocity)
        self.current_movement = "BACKWARD"

        self.get_logger().info("Sally moving backward!")

    def stop(self):

        velocity = Twist()
        velocity.linear.x = 0.0
        self.velocity_publisher.publish(velocity)
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