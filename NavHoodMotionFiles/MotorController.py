import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)

GPIO.setup(11,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(15,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)



p=GPIO.PWM(11,50)
direction = False
GPIO.output(13,direction)

lowLoopCount = 0
highLoopCount = 0
denominatorLowLoopCount = 0
denominatorHighLoopCount = 0
numeratorLowLoopCount = 0
numeratorHighLoopCount = 0
sleepTime = 0.001
count=0
while True:
        direction = False
        GPIO.output(13,direction)
        for x in xrange(0, 1):
                p.start(100)
                time.sleep(2.75)
                p.ChangeDutyCycle(0)
                p.stop()
                print(x)
        time.sleep(.5)

        direction = True
        GPIO.output(13,direction)
        for x in xrange(0, 1):
                p.start(100)
                time.sleep(2.75)
                p.ChangeDutyCycle(0)
                p.stop
                print(x)
        time.sleep(.5)

        direction = False
        GPIO.output(13,direction)
        for x in xrange(0,3):
                p.start(100)
                time.sleep(2.75/3)
                p.ChangeDutyCycle(0)
                p.stop()
                time.sleep(.5)
        time.sleep(.5)

        direction = True
        GPIO.output(13,direction)
        for x in xrange(0,3):
                p.start(100)
                time.sleep(2.75/3)
                p.ChangeDutyCycle(0)
                p.stop()
                time.sleep(.5)
        time.sleep(.5)


