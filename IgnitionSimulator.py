import RPi.GPIO as GPIO
import time

#variables
acc_pin = 16 #acc_pin simulator

GPIO.setmode(GPIO.BOARD)
GPIO.setup(acc_pin, GPIO.OUT)


def NormalStartCar():
    if GPIO.input(acc_pin)== 0:
        GPIO.output(acc_pin, 1)
        x=0
        while x<15:
            time.sleep(1)
            print(x)
            x+=1
    else:
        print("Already Started, Stop Car first")

def QuickStart():
    if GPIO.input(acc_pin)== 0:
        GPIO.output(acc_pin, 1)
    else:
        print("Already Started, Stop Car first")

def NormalStopCar():
    if GPIO.input(acc_pin)==1:
        GPIO.output(acc_pin, 0)
        x=0
        while x<15:
            time.sleep(1)
            print(x)
            x+=1
    else:
        print("Car already stopped, start car first")
def QuickStop():
    if GPIO.input(acc_pin)==1:
        GPIO.output(acc_pin, 0)
    else:
        print("Car already stopped, start car first")

def InterruptedStartCar():
	if GPIO.input(acc_pin)==0:
		GPIO.output(acc_pin, 1)
		time.sleep(3)
		GPIO.output(acc_pin, 0)
	else:
            print("Car already started, stop car first")
	
def StopEngineThenTurnAccessoriesOn():
	if GPIO.input(acc_pin)==1:
		GPIO.output(acc_pin, 0)
		time.sleep(3)
		GPIO.output(acc_pin, 1)
	else :
		print("Car already stopped, start car first")
def Shutdown():
    GPIO.cleanup()

blah = True;  
try:
    while blah:
            ignition_input = input("Start - Stop - Interrupt - StopAcc - QStart - QStop - Exit: \n")
            if ignition_input.lower()=="start":
                NormalStartCar()
                print(GPIO.input(acc_pin))
            elif ignition_input.lower()=="stop":
                NormalStopCar()
                print(GPIO.input(acc_pin))
            elif ignition_input.lower()=="interrupt":
                InterruptedStartCar()
                print(GPIO.input(acc_pin))
            elif ignition_input.lower()=="stopacc":
                StopEngineThenTurnAccessoriesOn()
                print(GPIO.input(acc_pin))
            elif ignition_input.lower()=="qstart":
                QuickStart()
            elif ignition_input.lower()=="qstop":
                QuickStop()
            elif ignition_input.lower()=="exit":
                Shutdown()
                blah = False
except KeyboardInterrupt:
                     Shutdown()