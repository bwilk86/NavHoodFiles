import time
import os
import RPi.GPIO as GPIO
# variables
open_direction = True
currentPos = 3
restorePos = 3
buttonDelay = .4
filePath = '/NavHoodFiles/NavHoodRestorePosition'

# GPIO
GPIO.setmode(GPIO.BCM)

# GPIO input pins
# accPin = 23#12
sleepyPiInputPin = 24
sleepyPiOutputPin = 25
tiltPin = 19  # 12
openPin = 20  # 15

# GPIO input setup
# GPIO.setup(accPin,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(sleepyPiInputPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(sleepyPiOutputPin, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(tiltPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(openPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# GPIO output pins
motor_en_pin = 21  # 11
motor_dir = 26  # 13

# GPIO output setup
GPIO.setup(motor_en_pin, GPIO.OUT)
GPIO.setup(motor_dir, GPIO.OUT)

# set motor_en_pin to PWM pin
motor_en = GPIO.PWM(motor_en_pin, 200)


def position_hood(start_pos, go_to_pos):
    # Determine how to position the hood
    print("Current Position: ", start_pos)
    print("Go To Position: ", go_to_pos)

    full_hood_sweep = 3.5
    quarter_hood_sweep = full_hood_sweep / 4
    eighth_hood_sweep = full_hood_sweep / 8
    motor_run_time = 0

    # Fully Closing the hood FROM any position
    if go_to_pos == 0:
        if start_pos == 1:
            motor_run_time = 2 * quarter_hood_sweep + eighth_hood_sweep
        elif start_pos == 2:
            motor_run_time = 3 * quarter_hood_sweep
        elif start_pos == 3:
            motor_run_time = 3 * quarter_hood_sweep + eighth_hood_sweep
        elif start_pos == 4:
            motor_run_time = full_hood_sweep
        move_hood(motor_run_time, not open_direction)
        start_pos = go_to_pos
        return start_pos

    # Fully Opening the hood TO any position
    if start_pos == 0:
        motor_run_time = 0
        if go_to_pos == 1:
            motor_run_time = 2 * quarter_hood_sweep
        elif go_to_pos == 2:
            motor_run_time = 2 * quarter_hood_sweep + eighth_hood_sweep
        elif go_to_pos == 3:
            motor_run_time = 3 * quarter_hood_sweep
        elif go_to_pos == 4:
            motor_run_time = full_hood_sweep
        move_hood(motor_run_time, open_direction)
        start_pos = go_to_pos
        return start_pos

    # Cycling between each of the tilt positions
    steps = go_to_pos - start_pos
    if steps < 0:
        print("2")
        steps = abs(steps)
        move_hood(steps * eighth_hood_sweep, not open_direction)
    elif steps > 0:
        print("3")
        move_hood(steps * eighth_hood_sweep, True)
    else:
        return
    return go_to_pos


def move_hood(run_time, direction):
    # Enable the motor to physically move the hood
    GPIO.output(motor_dir, direction)
    motor_en.start(100)
    time.sleep(run_time)
    motor_en.stop()


def set_restore_position_from_file():
    # get the position to restore the hood to from a position_file
    global filePath

    position_file = open(filePath, 'r')
    stored_pos = position_file.readline()
    return int(stored_pos)


def initialize_hood():
    # ensure that the hood is first closed, then set the restore position from a file,
    # then move the hood to the last stored point

    move_hood(3.5, not open_direction)
    stored_pos = set_restore_position_from_file()
    open_to_pos = position_hood(0, stored_pos)  # type: int
    return open_to_pos, stored_pos


def store_restore_position(pos_to_store):
    # stores the current position of the hood to a position_file.
    # Used to retain the hood position from last use/shutdown of vehicle.
    # commented lines are for the option of always storing the current position,
    # or adding some functionality for optionally storing the restorePos... not sure if useful
    # global restorePos
    global filePath

    position_file = open(filePath, 'w')
    # position_file.write(str(restorePos))
    position_file.write(str(pos_to_store))


def shutdown(pos_to_store):
    # function to occur when the ignition pin is turned off
    global motor_en
    move_hood(3.5, False)
    store_restore_position(pos_to_store)
    motor_en.stop()
    motor_en.ChangeDutyCycle(0)
    GPIO.cleanup()
    # os.system("sudo shutdown -h now")


try:

    current_pos, restore_pos = initialize_hood()

    # run while the SleepyPi is telling us to be on
    while not GPIO.input(sleepyPiInputPin):

        # Open button is pressed
        if GPIO.input(openPin):
            print("Open button pressed")
            print("Current Position: ", current_pos)
            if current_pos == 0:
                GPIO.output(motor_dir, open_direction)
                current_pos = position_hood(current_pos, restorePos)
                print("Restoring to position: ", restore_pos)
            else:
                restore_pos = current_pos
                print("Closing Hood, setting Restore Position to: ", restore_pos)
                current_pos = position_hood(current_pos, 0)
            time.sleep(buttonDelay)

        # Tilt button is pressed
        if GPIO.input(tiltPin):
            goTo = 0
            if current_pos == 0:
                time.sleep(.05)
            elif current_pos - 1 == 0:
                goTo = 4
                current_pos = position_hood(current_pos, goTo)
            else:
                goTo = currentPos - 1
                current_pos = position_hood(current_pos, goTo)
            time.sleep(buttonDelay)
    shutdown(current_pos)
    print("Exiting loop, performing cleanup")
except KeyboardInterrupt:
    shutdown(0)
