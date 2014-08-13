# import appropriate packages for use
import serial, pygame       

# important AX-12 constants
AX_WRITE_DATA = 3
AX_READ_DATA = 4
check = True

# Create the serial port object, apply settings, and open the port.
s = serial.Serial()
s.baudrate = 9600
s.port = 4
s.open()

# The set_map function will set a value from w-x t--> y-z.  example: 0-180 --> 0-2048
def set_map( x,  in_min,  in_max,  out_min,  out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Write to the registers with the index(ID) of the motor, the registery value, and values to write
def setReg(index,reg,values):
    length = 3 + len(values)
    checksum = 255-((index+length+AX_WRITE_DATA+reg+sum(values))%256)          
    s.write(chr(0xFF)+chr(0xFF)+chr(index)+chr(length)+chr(AX_WRITE_DATA)+chr(reg))
    for val in values:
        s.write(chr(val))
    s.write(chr(checksum))

# Used to retrieve the values from the motors registry.  example: Register 43 returns current temperature
def getReg(index, regstart, rlength):
    s.flushInput()   
    checksum = 255 - ((6 + index + regstart + rlength)%256)
    s.write(chr(0xFF)+chr(0xFF)+chr(index)+chr(0x04)+chr(AX_READ_DATA)+chr(regstart)+chr(rlength)+chr(checksum))
    vals = list()
    s.read()   # 0xff - reserved
    s.read()   # 0xff - reserved
    s.read()   # ID
    length = ord(s.read()) - 1
    s.read()   # toss error    
    while length > 0:
        vals.append(ord(s.read()))
        length = length - 1
    if rlength == 1:
        return vals[0]
    return vals

# Initialize the PyGame package 
pygame.joystick.init()
pygame.display.init()

# use the joystick above to create a new object - starts at 0 and moves up.
joystick = pygame.joystick.Joystick(0)

#now you need to inistialze the joystick
joystick.init()

# Returns the name of the joystick.  Will be used later for error checking
name = joystick.get_name()
print "Name:", name


# Continue to run until exited by the user pressing the button 3(Y)
while check:
        pan = round((joystick.get_axis(0) *90 + 90),2) 
        tilt = round((joystick.get_axis(1) * 90 + 90),2)
        throttle = round((joystick.get_axis(3) * 90 +90),2)
        direction = round((joystick.get_axis(4) * 90 +90),2)
        print("Pan: %f, Tilt: %f, Throttle: %f, Direction: %f" % (pan,tilt,throttle,direction) )
        
        button = joystick.get_button(3)
        if button == 1:
                check = False
                
# Need to add some sort of case switching here. 
        # define the forward and reverse directions
        if throttle <= 65:
            right = int(set_map(throttle,0,90,2047,1025))
            left = int(set_map(throttle, 0,90,1023,1))
            setReg(1,32,((right%256),(right>>8)))
            setReg(2,32,((left%256),(left>>8)))
        elif throttle >= 115:
            right = int(set_map(throttle,90,180,1,1023))
            left = int(set_map(throttle, 90,180,1025,2047))
            setReg(1,32,((right%256),(right>>8)))
            setReg(2,32,((left%256),(left>>8)))
        else:
            setReg(1,32,((0%256),(0>>8)))
            setReg(2,32,((0%256),(0>>8)))



        # define the left and right directions
        if direction <= 65:
            right = int(set_map(direction,0,90, 1023,1))
            left = int(set_map(direction,0,90,1023,1))
            setReg(1,32,((right%256),(right>>8)))
            setReg(2,32,((left%256),(left>>8)))
        elif direction >=115:
            right= int(set_map(direction,90,180,1025,2047))
            left = int(set_map(direction,90,180,1025,2047))
            setReg(1,32,((right%256),(right>>8)))
            setReg(2,32,((left%256),(left>>8)))
        else:
            setReg(1,32,((0%256),(0>>8)))
            setReg(2,32,((0%256),(0>>8)))
            
        # pull the next event - if not used the joystick will get ahead of the program



        # define the forward and reverse tilt

        # define the left and right pan

        # define the gripper movement
        
        
        pygame.event.pump()


# use the close port for cleanup and to make sure the port doesn't deadlock
print "exiting..."
s.close()
