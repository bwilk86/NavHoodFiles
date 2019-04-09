import time
import os
# noinspection SpellCheckingInspection
import RPi.GPIO as GPIO
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


# GPIO
# GPIO.GetMode - 11=BCM, 10=Board
GPIO.setmode(GPIO.BCM)

# variables
open_direction = True
currentPos = 0

restorePos = 0
hoodOpen = False

buttonDelay = .4
filePath = '/NavHoodFiles/NavHoodRestorePosition'
file_name = '/Settings/settings.xml'

# GPIO input pins
# accPin = 23#12
shutoffSignal = 24
powerSignal = 25
tiltPin = 19  # 12
openPin = 20  # 15
# GPIO output pins
motor_en_pin = 21  # 11
motor_dir = 26  # 13


def set_program_variables(settings_element_tree):
    global open_direction, \
        restorePos, buttonDelay, file_name, \
        shutoffSignal, powerSignal, tiltPin, \
        openPin, motor_en_pin, motor_dir, hoodOpen

    # set the board mode to assign variables
    if GPIO.getmode() == 11:
        mode = "BCM"
    else:
        mode = "Board"
    for pin in settings_element_tree.Settings.iter("Pins"):
        if pin.Name == "ShutoffSignal":
            shutoffSignal = pin.Number.get(mode)
        elif pin.Name == "TiltPin":
            tiltPin = pin.Number.get(mode)
        elif pin.Name == "OpenPin":
            openPin = pin.Number.get(mode)
        elif pin.Name == "PowerSignal":
            powerSignal = pin.Number.get(mode)
        elif pin.Name == "MotorEnabled":
            motor_en_pin = pin.Number.get(mode)
        elif pin.Name == "MotorDirection":
            motor_dir = pin.Number.get(mode)

    for defSetting in settings_element_tree.Settings.iter("DefaultSettings"):
        if defSetting.name == "OpenDirection":
            open_direction = defSetting.Value
        elif defSetting.name == "ButtonDelay":
            buttonDelay = defSetting.Value

    for storedValue in settings_element_tree.Settings.iter("StoredValue"):
        if storedValue.name == "RestorePosition":
            restorePos = storedValue.Value
        elif storedValue.name == "HoodOpen":
            hoodOpen = storedValue.Value


def set_pin_directions():
    # GPIO input setup
    # GPIO.setup(accPin,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(shutoffSignal, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(powerSignal, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(tiltPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(openPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # GPIO output setup
    GPIO.setup(motor_en_pin, GPIO.OUT)
    GPIO.setup(motor_dir, GPIO.OUT)
    # set motor_en_pin to PWM pin


def load_settings_from_file(file_name_string):
    xml_tree = ET.parse(file_name_string)
    root = xml_tree.getiterator()
    return xml_tree, root


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


def initialize_hood(restore_position, hood_open):
    # ensure that the hood is first closed, then set the restore position from a file,
    # then move the hood to the last stored point
    # int, bool

    move_hood(3.5, not open_direction)
    if hood_open:
        open_to_pos = position_hood(0, restore_position)
        return open_to_pos  # type: int
    else:
        return 0


def store_restore_position(pos_to_store):
    # stores the current position of the hood to a position_file.
    # Used to retain the hood position from last use/shutdown of vehicle.
    global filePath

    position_file = open(filePath, 'w')
    position_file.write(str(pos_to_store))


def shutdown(element_tree, root, current_position, restore_position):
    # function to occur when the ignition pin is turned off
    global motor_en, file_name

    for stored_value in root.StoredValues:
        if stored_value.name == "HoodOpen":
            if int(current_position) == 0:
                stored_value.Value = False
            else:
                stored_value.Value = True
        elif stored_value.name == "RestorePosition":
            stored_value.Value = int(restore_position)

    move_hood(3.5, False)
    element_tree.write(file_name)
    motor_en.stop()
    motor_en.ChangeDutyCycle(0)
    GPIO.cleanup()
    # os.system("sudo shutdown -h now")


try:
    # TODO: write file write for XML settings for booting
    tree, settings = load_settings_from_file(file_name)

    set_program_variables(settings)

    set_pin_directions()
    # set motor_en_pin to PWM pin
    motor_en = GPIO.PWM(motor_en_pin, 200)

    currentPos = initialize_hood(restorePos, hoodOpen)

    # run while the SleepyPi is telling us to be on
    while not GPIO.input(shutoffSignal):

        # Open button is pressed
        if GPIO.input(openPin):
            print("Open button pressed")
            print("Current Position: ", currentPos)
            if currentPos == 0:
                GPIO.output(motor_dir, open_direction)
                currentPos = position_hood(currentPos, restorePos)
                print("Restoring to position: ", restorePos)
            else:
                restorePos = currentPos
                print("Closing Hood, setting Restore Position to: ", restorePos)
                currentPos = position_hood(currentPos, 0)
            time.sleep(buttonDelay)

        # Tilt button is pressed
        if GPIO.input(tiltPin):
            goTo = 0
            if currentPos == 0:
                time.sleep(.05)
            elif currentPos - 1 == 0:
                goTo = 4
                currentPos = position_hood(currentPos, goTo)
            else:
                goTo = currentPos - 1
                currentPos = position_hood(currentPos, goTo)
            time.sleep(buttonDelay)
    shutdown(tree, settings, currentPos, restorePos)
    print("Exiting loop, performing cleanup")
except KeyboardInterrupt:
    shutdown(tree, settings, currentPos, restorePos)
