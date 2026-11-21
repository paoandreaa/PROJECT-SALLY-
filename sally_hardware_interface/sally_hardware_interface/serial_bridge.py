#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist
from rclpy.parameter import Parameter
from sally_msgs.msg import ServoHead
import RPi.GPIO as GPIO
import time

import board
import adafruit_pca9685
import adafruit_motor.servo

class serial_bridge(Node):
    def __init__(self):
        super().__init__("sally_hardware")

        self.get_parameter()

        self.rh_ultra_pub = self.create_publisher(
            Float32,
            '/sally/rh_dist',
            10
        )

        # INICIO LA PCA
        i2c = board.I2C()
        self.pca =  adafruit_pca9685.PCA9685(i2c)
        self.pca.frequency = 50

        # CONECTO EL SERVO AL CANAL
        self.servo = adafruit_motor.servo.Servo(self.pca.channels[self.servo_chanel])

        # SE SUSCRIBE AL TOPIC
        self.servo_subscription = self.create_subscription(
            ServoHead,
            "/sally/servo_command",
            self.angle_callback(),
            10
        )

        self.motor_subscription = self.create_subscription(
            Twist,
            "/sally/cmd_vel",
            self.rotarion_callback(),
            10
        )

        self.get_logger().info(
            "Sally servo driver started!"
        )

    def get_parameters(self):
        self.declare_parameter('trig_ultra', 11)
        self.declare_parameter('echo_ultra', 8)
        self.declare_parameter('servo_chanel', 2)
        self.declare_parameter('in1', 26)
        self.declare_parameter('ena', 4)
        self.declare_parameter('in2', 21)
        self.declare_parameter('in4', 18)
        self.declare_parameter('enb', 17)
        self.declare_parameter('in3', 27)

        self.set_parameters([
            Parameter('trig_ultra', Parameter.Type.INTEGER, 11),
            Parameter('echo_ultra', Parameter.Type.INTEGER, 8),
            Parameter('servo_chanel', Parameter.Type.INTEGER, 2),
            Parameter('in1', Parameter.Type.INTEGER, 26),
            Parameter('ena', Parameter.Type.INTEGER, 4),
            Parameter('in2', Parameter.Type.INTEGER, 21),
            Parameter('in4', Parameter.Type.INTEGER, 18),
            Parameter('enb', Parameter.Type.INTEGER, 17),
            Parameter('in3', Parameter.Type.INTEGER, 27),
            ])


    def rh_ultra(self):
        GPIO.setmode(GPIO.BCM)

        GPIO.setmode(self.trig_ultra, GPIO.OUT)
        GPIO.setmode(self.echo_ultra, GPIO.IN)

        #inicializar sensor
        GPIO.output(self.trig_ultra, False)
        time.sleep(0.2)

        GPIO.output(self.trig_ultra, True)
        time.sleep(0.00001)
        GPIO.output(self.trig_ultra, False)

        #Medir duracion del pulso
        while GPIO.input(self.echo_ultra)==0:
            pulse_start = time.time()

        while GPIO.input(self.echo_ultra)==1:
            pulse_end= time.time()

        pulse_duration = pulse_start - pulse_end

        self.rh_ultra_pub.publish(pulse_duration)

    def rotarion_callback(self, velocity):
        #inicializar los GPIO
        GPIO.setmode(GPIO.BCM)

        GPIO.setmode(self.in1, GPIO.OUT)
        GPIO.setmode(self.ena, GPIO.OUT)
        GPIO.setmode(self.in2, GPIO.OUT)

        GPIO.setmode(self.in4, GPIO.OUT)
        GPIO.setmode(self.enb, GPIO.OUT)
        GPIO.setmode(self.in3, GPIO.OUT)

        #Establecer los pwm
        pwm_motor1 = GPIO.PWM(self.ena, 1000)
        pwm_motor1.start(0)

        pwm_motor2 = GPIO.PWM(self.enb, 1000)
        pwm_motor2.start(0)

        #Recibir intrucciones
        self.pwm_motor1.ChangeDutyCycle(velocity.linear.x)
        self.pwm_motor2.ChangeDutyCycle(velocity.linear.x)

        if(velocity.angular.x>0):
            GPIO.output(self.in1, True)
            GPIO.output(self.in2, False)

            GPIO.output(self.in4, False)
            GPIO.output(self.in3, True)
        elif(velocity.angular.x<0):
            GPIO.output(self.in1, False)
            GPIO.output(self.in2, True)

            GPIO.output(self.in1, True)
            GPIO.output(self.in2, False)
        elif(velocity.angular.x):
            GPIO.output(self.in1, True)
            GPIO.output(self.in2, True)

            GPIO.output(self.in1, True)
            GPIO.output(self.in2, True)


    def angle_callback(self, message):

        angle = float(message.servo1)

        # VERFICA SI EL ANGULO ES VÁLIDO
        if not 0.0 <= angle <= 180.0:
            self.get_logger().warning(
                f"Invalid angle received: {angle.servo1}"
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
    node = serial_bridge()
    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()

