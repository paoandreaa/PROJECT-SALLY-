import rclpy
from rclypy.node import Node
from std_msgs.msg import float32
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

TRIG = 11
ECHO = 8

GPIO.setmode(TRIG, GPIO.OUT)
GPIO.setmode(ECHO, GPIO.IN)



class SerialUltra(Node):
    def __init__(self):
        super().__init__("ultra")
        self.ultra_pub =  self.create_publisher( 
            float32,
            'dist',
            10
        )
        #inicializar sensor
        GPIO.output(TRIG, False)
        time.sleep(0.2)

        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        #Medir la duracion del pulso
        while GPIO.input(ECHO)==0:
            pulse_start = time.time()

        while GPIO.input(ECHO)==1:
            pulse_end = time.time()

        pulse_duration = pulse_start - pulse_end

        #Pasar velocidad del sonido a distancia -- m a cm (34300) y dividido en 2
        distance = pulse_duration * 17150

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



