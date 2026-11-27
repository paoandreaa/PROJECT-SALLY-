#!/usr/bin/env python3


import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist
from rclpy.parameter import Parameter
from sally_msgs.msg import ServoHead, CarMovement
import RPi.GPIO as GPIO
import time

import board
import adafruit_pca9685
import adafruit_motor.servo

class serial_bridge(Node):
    def __init__(self):
        super().__init__("sally_hardware")

        self.declare_parameter('trig_ultra', 11)
        self.declare_parameter('echo_ultra', 8)
        self.declare_parameter('servo2_chanel', 2)
        self.declare_parameter('servo1_chanel', 1)
        self.declare_parameter('servo0_chanel', 0)
        self.declare_parameter('in1', 26)
        self.declare_parameter('ena', 4)
        self.declare_parameter('in2', 21)
        self.declare_parameter('in4', 18)
        self.declare_parameter('enb', 17)
        self.declare_parameter('in3', 27)

        self.thing_parm()

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.trig_ultra, GPIO.OUT)
        GPIO.setup(self.echo_ultra, GPIO.IN)

        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.ena, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)

        GPIO.setup(self.in4, GPIO.OUT)
        GPIO.setup(self.enb, GPIO.OUT)
        GPIO.setup(self.in3, GPIO.OUT)

        self.pwm_motor1 = GPIO.PWM(self.ena, 1000)
        self.pwm_motor1.start(0)

        self.pwm_motor2 = GPIO.PWM(self.enb, 1000)
        self.pwm_motor2.start(0)

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
        self.servo2 = adafruit_motor.servo.Servo(self.pca.channels[self.servo2_chanel])
        self.servo1 = adafruit_motor.servo.Servo(self.pca.channels[self.servo1_chanel])
        self.servo0 = adafruit_motor.servo.Servo(self.pca.channels[self.servo0_chanel])

        # SE SUSCRIBE AL TOPIC
        self.servo_subscription = self.create_subscription(
            ServoHead,
            "/sally/servo_command",
            self.angle_callback,
            10
        )

        self.motor_subscription = self.create_subscription(
            CarMovement,
            "/sally/cmd_vel",
            self.rotarion_callback,
            10
        )

        self.get_logger().info(
            "Sally servo driver started!"
        )

        self.timer = self.create_timer(0.1, self.rh_ultra)

    def thing_parm(self):

        self.trig_ultra = self.get_parameter('trig_ultra').value
        self.echo_ultra = self.get_parameter('echo_ultra').value
        self.servo2_chanel = self.get_parameter('servo2_chanel').value
        self.servo1_chanel = self.get_parameter('servo1_chanel').value
        self.servo0_chanel = self.get_parameter('servo0_chanel').value
        self.in1 = self.get_parameter('in1').value
        self.ena = self.get_parameter('ena').value
        self.in2 = self.get_parameter('in2').value
        self.in4 = self.get_parameter('in4').value
        self.enb = self.get_parameter('enb').value
        self.in3 = self.get_parameter('in3').value
        
    # end def


    def rh_ultra(self):
        

        #inicializar sensor
        GPIO.output(self.trig_ultra, False)
        time.sleep(0.1)

        GPIO.output(self.trig_ultra, True)
        time.sleep(0.00001)
        GPIO.output(self.trig_ultra, False)

        #Medir duracion del pulso
        while GPIO.input(self.echo_ultra)==0:
            pulse_start = time.time()

        while GPIO.input(self.echo_ultra)==1:
            pulse_end= time.time()
        pulse_duration = Float32()
        duration = pulse_end - pulse_start
        pulse_duration.data = float(duration)

        self.rh_ultra_pub.publish(pulse_duration)

    def rotarion_callback(self, velocity):

        speed = max(0.0, min(abs(velocity.speed) * 100, 100.0))
        if(velocity.direction=="RIGHT"):
            angle0 = 175.0
        elif(velocity.direction=="LEFT"):
            angle0 = 5.0
        elif(velocity.direction=="STRAIGHT"):
            angle0 = 90.0
        else:
            angle0 = 90.0

        if not 0.0 <= angle0 <= 180.0:
            self.get_logger().warning(
                f"Invalid angle received: {angle0}"
            )
            return

        # MUEVE EL SERVO
        self.servo0.angle = angle0

        self.get_logger().info(
            f"Servo moved to {angle0} degrees"
        )

        #Mueve motores DC
        if(velocity.rute=="FORWARD"):
            GPIO.output(self.in1, True)
            GPIO.output(self.in2, False)

            GPIO.output(self.in4, False)
            GPIO.output(self.in3, True)

            self.pwm_motor1.ChangeDutyCycle(speed)
            self.pwm_motor2.ChangeDutyCycle(speed)
        elif(velocity.rute=="BACKWARD"):
            GPIO.output(self.in1, False)
            GPIO.output(self.in2, True)

            GPIO.output(self.in4, True)
            GPIO.output(self.in3, False)

            self.pwm_motor1.ChangeDutyCycle(speed)
            self.pwm_motor2.ChangeDutyCycle(speed)
        elif(velocity.rute=="STOP"):
            GPIO.output(self.in1, True)
            GPIO.output(self.in2, True)

            GPIO.output(self.in4, True)
            GPIO.output(self.in3, True)

            self.pwm_motor1.ChangeDutyCycle(0)
            self.pwm_motor2.ChangeDutyCycle(0)


    def angle_callback(self, message):

        angle2 = float(message.servo1)
        angle1 = float(message.servo2)

        # VERFICA SI EL ANGULO ES VÁLIDO
        if not 0.0 <= angle2 <= 180.0:
            self.get_logger().warning(
                f"Invalid angle received: {angle2}"
            )
            return

        if not 0.0 <= angle1 <= 180.0:
                    self.get_logger().warning(
                        f"Invalid angle received: {angle1}"
                    )
                    return

        # MUEVE EL SERVO
        self.servo2.angle = angle2

        self.get_logger().info(
            f"Servo moved to {angle2} degrees"
        )

        self.servo1.angle = angle1

        self.get_logger().info(
            f"Servo moved to {angle1} degrees"
        )


    def destroy_node(self):
        self.pwm_motor1.stop()
        self.pwm_motor2.stop()
        self.pca.deinit()
        GPIO.cleanup()
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