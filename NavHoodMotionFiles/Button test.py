import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)

GPIO.setup(15,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

while True:
    if (GPIO.input(15) ==1):
        print("GPIO 15 went high when button pressed")
        time.sleep(.25)
        
