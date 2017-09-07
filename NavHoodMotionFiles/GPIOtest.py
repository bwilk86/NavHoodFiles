import RPi.GPIO as GPIO
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)

GPIO.output(11,1)
GPIO.output(13,1)
GPIO.output(11,0)
GPIO.output(13,0)
GPIO.cleanup()
