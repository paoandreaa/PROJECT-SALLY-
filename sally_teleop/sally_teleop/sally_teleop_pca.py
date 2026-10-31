
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import board

import adafruit_pca9685
import adafruit_motor.servo


class SallyServoDriver(Node):

    def __init__(self):
        super().__init__("sally_servo_driver")

        # INICIO LA PCA
        i2c = board.I2C()
        self.pca =  adafruit_pca9685.PCA9685(i2c)
        self.pca.frequency = 50

        # CONECTO EL SERVO AL CANAL
        self.servo = adafruit_motor.servo.Servo(self.pca.channels[2])

        # SE SUSCRIBE AL TOPIC
        self.subscription = self.create_subscription(
            Float32,
            "/sally/servo_command",
            self.angle_callback,
            10
        )

        self.get_logger().info(
            "Sally servo driver started!"
        )

    def angle_callback(self, message):

        angle = float(message.data)

        # VERFICA SI EL ANGULO ES VÁLIDO
        if not 0.0 <= angle <= 180.0:
            self.get_logger().warning(
                f"Invalid angle received: {angle}"
            )
            return

        # MUEVE EL SERVO
        self.servo.angle = angle

        self.get_logger().info(
            f"Servo moved to {angle} degrees"
        )

    def destroy_node(self):
        self.pca.deinit()
        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = SallyServoDriver()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()