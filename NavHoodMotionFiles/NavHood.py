import RPi.GPIO as GPIO
import time
import os

#variables
curDirection = True
currentPos = 3
restorePos = 3
buttonDelay = .4
filePath = '/home/pi/Desktop/MotorController/NavHoodRestorePosition'

#GPIO 
GPIO.setmode(GPIO.BCM)

#GPIO input pins
#accPin = 23#12
sleepyPiInputPin = 24
sleepyPiOutputPin = 25
tiltPin = 18#12
openPin = 22#15

#GPIO input setup
#GPIO.setup(accPin,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(sleepyPiInputPin,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(sleepyPiOutputPin,GPIO.OUT,pull_up_down=GPIO.PUD_UP)
GPIO.setup(tiltPin,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(openPin,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#GPIO output pins
motor_en_pin = 11
motor_dir = 13

#GPIO output setup
GPIO.setup(motor_en_pin,GPIO.OUT)
GPIO.setup(motor_dir,GPIO.OUT)

#set motor_en_pin to PWM pin
motor_en = GPIO.PWM(motor_en_pin, 50)

def PositionHood(goToPos):
    #Determine how to position the hood
    global currentPos
    print "Current Position: ", currentPos
    print "Go To Position: ", goToPos
    
    fullHoodSweep = 3.5
    quarterHoodSweep = fullHoodSweep/4
    eigthHoodSweep = fullHoodSweep/8
    
    #Fully Closing the hood FROM any position        
    if goToPos == 0:
        if currentPos==1:
            motorRunTime = 2*quarterHoodSweep + eigthHoodSweep
        elif currentPos==2:
            motorRunTime = 3*quarterHoodSweep 
        elif currentPos==3:
            motorRunTime= 3*quarterHoodSweep + eigthHoodSweep
        elif currentPos==4:
            motorRunTime=fullHoodSweep
        MoveHood(motorRunTime, False)
        currentPos= goToPos
        return
    
    #Fully Opening the hood TO any position
    if currentPos == 0:
        if goToPos==1:
            motorRunTime = 2*quarterHoodSweep
        elif goToPos==2:
            motorRunTime = 2*quarterHoodSweep + eigthHoodSweep
        elif goToPos==3:
            motorRunTime= 3*quarterHoodSweep
        elif goToPos==4:
            motorRunTime=fullHoodSweep
        MoveHood(motorRunTime, True)
        currentPos = goToPos
        return
    
    #Cycling between each of the tilt positions
    steps = goToPos-currentPos
    if steps < 0:
        print "2"
        steps = abs(steps)
        MoveHood(steps*eigthHoodSweep, False)
    elif steps > 0:
        print "3"
        MoveHood(steps*eigthHoodSweep, True)
    else:
        return
    currentPos= goToPos

def MoveHood(runTime, direction):
    #Enable the motore to physically move the hood
    GPIO.output(motor_dir,direction)
    motor_en.start(100)
    time.sleep(runTime)
    motor_en.stop()
    
def SetRestorePositionFromFile():
    #get the position to restore the hood to from a file
    global filePath
    global restorePos

    file = open(filePath, 'r')
    storedPos = file.readline()
    restorePos = int(storedPos)

def InitializeHood():
    #ensure that the hood is first closed, then set the restore position from a file,
    #then move the hood to the last stored point
    global currentPos
    global restorePos

    MoveHood(3.5, False)
    currentPos = 0
    SetRestorePositionFromFile()
    PositionHood(restorePos)

def StoreRestorePosition():
    #stores the current position of the hood to a file. 
    #Used to retain the hood position from last use/shutdown of vehicle.
    #commented lines are for the option of always storing the current position,
    #or adding some functionality for optionally storing the restorePos... not sure if useful
    #global restorePos
    global currentPos
    global filePath

    #if currentPos != 0:
    #   restorePos = currentPos

    file = open(filePath, 'w')
    #file.write(str(restorePos))
    file.write(str(currentPos))
    
def ShutDown():
    #function to occur when the ignition pin is turned off
    global motor_en
    MoveHood(3.5, False)
    StoreRestorePosition()
    motor_en.stop()
    motor_en.ChangeDutyCycle(0)
    GPIO.cleanup()
    os.system("sudo shutdown -h now")
    
try:
    InitializeHood()

    #run while the accessories are on
    while GPIO.input(sleepyPiInputPin) != True:
        
        #Open button is pressed
        if GPIO.input(openPin) == True:
            print"Open button pressed"
            print"Current Position: ", currentPos
            if currentPos == 0:
                GPIO.output(motor_dir,curDirection)
                PositionHood(restorePos)
                print"Restoring to position: ", restorePos
            else:
                restorePos=currentPos
                print"Closing Hood, setting Restore Position to: ", restorePos
                PositionHood(0)
            time.sleep(buttonDelay)
    
        #Tilt button is pressed
        if GPIO.input(tiltPin) == True:
            goTo = 0
            if currentPos==0:
                time.sleep(.05)
            elif currentPos-1 == 0:
                goTo=4
                PositionHood(goTo)
            else:
                goTo = currentPos-1
                PositionHood(goTo)
            time.sleep(buttonDelay)
    ShutDown()
    print "Exiting loop, performing cleanup"
except KeyboardInterrupt:
    ShutDown()

