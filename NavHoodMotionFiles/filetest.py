file = open('/home/pi/Desktop/MotorController/NavHoodRestorePosition', 'r')
print file
restorePos = file.readline()
print restorePos
file = open('/home/pi/Desktop/MotorController/NavHoodRestorePosition', 'w')
file.write("3")
file = open('/home/pi/Desktop/MotorController/NavHoodRestorePosition', 'r')
print file
restorePos = file.readline()
print restorePos
number = 3
if number == int(restorePos):
    print "equals"
else:
    print "not equals"
