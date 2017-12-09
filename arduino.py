#Brent Turner - CSC 400 independent project - Arduino Oscilloscope
import sys
import glob
import serial
import io
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import time
import numpy as np


#Gets all availabe serial Ports
def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result #returns a list



#get the current port list
portList = serial_ports()

#If the list has multiple options
if(len(portList) > 1):
    print("Please type the port you desire")
    for port in portList:
        print(port)
    selectedPort = raw_input()
    
#If Only one Option - default for the user
elif(len(portList) == 1):
    selectedPort = portList[0]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ START SERIAL LINK WITH ARDUINO ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Gets all the data from the Serial Port at a Baud Rate of 115200    --- Difference between Baud Rate & Bit Rate http://www.electronicdesign.com/communications/what-s-difference-between-bit-rate-and-baud-rate
ser = serial.Serial(selectedPort, 115200,timeout=0, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)

''' <Note>

Do to the wonderful fact that serial.readline() was made to eliminate the '\r' or carriage return, I was forced to find a method to which
I would be able to still implement it, and that is because it is required to read my serial port with EOL parameters; therefore, this
line came into play.
    </Note>
''' 
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser)) 


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GET THE GRAPH SETUP ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#https://matplotlib.org/devdocs/gallery/animation/strip_chart_demo.html

style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)


def animate(i):
    xs = []
    ys = []
    
    whiteSpace = sio.readline() #capture the whitespace
    data = sio.readline()

    #Check for all the white space
    while(whiteSpace == data):
        data = sio.readline() #Print to the Regular console the readings
        
    for i in range (0, 250):
        try:
            data = sio.readline()
            attempt = float(data)
            xs.append(i)
            ys.append(attempt)
            
        #Failed to create float
        except:
            print("Failed to create float: " + data)
        
    ax1.clear()
    ax1.plot(xs, ys)



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ START GETTING DATA FOREVER! ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

while True:
    try:   
        ani = animation.FuncAnimation(fig, animate)
        plt.show()

    except KeyboardInterrupt:
        break

ser.close()
