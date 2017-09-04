import RPi.GPIO as GPIO
import time

#variables
acc_pin = 16 #acc_pin simulator

GPIO.setup(acc_pin, GPIO.OUT)

def NormalStartCar():
	if(GPIO.input(acc_pin) == 0)
		GPIO.output(acc_pin, 1)
		time.sleep(15)
	else
		print "Already Started, Stop Car first"

def NormalStopCar():
	if(GPIO.input(acc_pin) == 1)
		GPIO.output(acc_pin, 0)
		time.sleep(15)
	else
		print "Car already stopped, start car first"
def InterruptedStartCar():z
	if(GPIO.input(acc_pin) == 0)
		GPIO.ouput(acc_pin, 1)
		time.sleep(3)
		GPIO.output(acc_pin, 0)
	else
		print "Car already started, stop car first"
	
def StopEngineThenTurnAccessoriesOn:
	if(GPIO.input(acc_pin) == 1)
		GPIO.output(acc_pin, 0)
		time.sleep(3)
		GPIO.output(acc_pin, 1)
	else 
		print "Car already stopped, start car first"
def Shutdown:
    GPIO.cleanup()
    
try:
    while True:
	ignition_input = input("Start/Stop/Interrupt/StopAcc")
	if(ignition_input.lower == "start")
            NormalStartCar()
	elif(ignition_input.lower == "stop")
            NormalStopCar()
	elif(ignition_input.lower == "interrupt")
            InterruptedStartCar()
	elif(ignition_input.lower == "stopacc")
            StopEngineThenTurnAccessoriesOn()
except KeyboardInterrupt:
                     Shutdown()