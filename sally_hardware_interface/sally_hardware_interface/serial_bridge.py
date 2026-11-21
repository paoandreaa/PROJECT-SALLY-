#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sally_msgs.msg import SallyServo
from geometry_msgs.msg import Twist

import RPi.GPIO as GPIO
import board

import adafruit_pca9685
import adafruit_motor.servo


class SallyPhysicalDriver(Node):

    def __init__(self):
        super().__init__("sally_physical_driver")

        # 1. INICIALIZAR LA PCA9685 PARA LOS SERVOS
        i2c = board.I2C()
        self.pca = adafruit_pca9685.PCA9685(i2c)
        self.pca.frequency = 50

        # CONECTAR SERVOS A LOS CANALES 2 Y 3
        self.servo_1 = adafruit_motor.servo.Servo(self.pca.channels[2])
        self.servo_2 = adafruit_motor.servo.Servo(self.pca.channels[3])

        # 2. DEFINIR LOS PINES GPIO DEL MOTOR (BCM)
        self.motor_en = 4
        self.motor_in1 = 26
        self.motor_in2 = 21

        # CONFIGURACIÓN FÍSICA DE LOS MOTORES
        self.setup_motors()

        # VELOCIDAD MÁXIMA Y LÍMITE PWM
        self.max_linear_speed = 0.2
        self.max_duty_cycle = 40.0

        # 3. SUSCRIPCIONES EN ROS 2
        # Suscripción para los movimientos de la cabeza
        self.servo_subscription = self.create_subscription(
            SallyServo,
            "/sally/servo_command",
            self.angle_callback,
            10
        )

        # Suscripción para la tracción de las ruedas (recibe de SallyMovement)
        self.velocity_subscription = self.create_subscription(
            Twist,
            "/sally/cmd_vel",
            self.velocity_callback,
            10
        )

        self.get_logger().info("Sally Physical Driver (Servos + Motors) started!")

    def setup_motors(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.motor_en, GPIO.OUT)
        GPIO.setup(self.motor_in1, GPIO.OUT)
        GPIO.setup(self.motor_in2, GPIO.OUT)

        self.pwm = GPIO.PWM(self.motor_en, 1000)
        self.pwm.start(0)

    # CONTROL DE LOS SERVOS DE LA CABEZA
    def angle_callback(self, message):
        angle_1 = float(message.servo_1)
        angle_2 = float(message.servo_2)

        if not 0.0 <= angle_1 <= 180.0:
            self.get_logger().warning(f"Invalid servo 1 angle: {angle_1}")
            return

        if not 0.0 <= angle_2 <= 180.0:
            self.get_logger().warning(f"Invalid servo 2 angle: {angle_2}")
            return

        self.servo_1.angle = angle_1
        self.servo_2.angle = angle_2

        self.get_logger().info(f"Servo 1: {angle_1} | Servo 2: {angle_2}")

    # CONTROL DE VELOCIDAD DE LAS RUEDAS (RECIBE CMD_VEL)
    def velocity_callback(self, message):
        speed = message.linear.x

        if speed == 0.0:
            self.motor_detener()
            return

        # Calcular ciclo de trabajo 
        duty_cycle = (abs(speed) / self.max_linear_speed) * self.max_duty_cycle
        duty_cycle = min(duty_cycle, self.max_duty_cycle)

        if speed > 0:
            self.motor_adelante(duty_cycle)
        elif speed < 0:
            self.motor_atras(duty_cycle)

    # MÉTODOS DE POTENCIA PARA EL PUENTE H
    def motor_adelante(self, velocidad):
        GPIO.output(self.motor_in1, GPIO.HIGH)
        GPIO.output(self.motor_in2, GPIO.LOW)
        self.pwm.ChangeDutyCycle(velocidad)

    def motor_atras(self, velocidad):
        GPIO.output(self.motor_in1, GPIO.LOW)
        GPIO.output(self.motor_in2, GPIO.HIGH)
        self.pwm.ChangeDutyCycle(velocidad)

    def motor_detener(self):
        self.pwm.ChangeDutyCycle(0)
        GPIO.output(self.motor_in1, GPIO.LOW)
        GPIO.output(self.motor_in2, GPIO.LOW)

    # LIBERAR HARDWARE DE FORMA SEGURA AL APAGAR
    def destroy_node(self):
        self.motor_detener()
        self.pwm.stop()
        GPIO.cleanup()
        self.pca.deinit()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = SallyPhysicalDriver()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()