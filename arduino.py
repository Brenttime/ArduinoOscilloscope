#Brent Turner - CSC 400 independent project - Arduino Oscilloscope
import sys
import glob
import serial
import io
import time
import numpy as np
import pyqtgraph as pg

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
    selectedPort = input()

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
try:
    plt = pg.plot()
    bufferSize = 1000
    data = np.zeros(bufferSize)
    curve = plt.plot()
    line = plt.addLine(x=0)
    plt.setRange(xRange=[0, bufferSize], yRange=[-15, 15])
    i = 0
except:
    print("Graph Config Error")

def update():
    global data, curve, line, i

    whiteSpace = sio.readline() #capture the whitespace
    readData = sio.readline()

    #Check for all the white space
    while(whiteSpace == data):
        readData = sio.readline() #Print to the Regular console the readings
        print(ReadData)

    n = 1  # update 1 samples per iteration

    try:
        reading = float(sio.readline()) * 3.28 #The value my voltage divider works at (6.8k and 3.3k ohlm resisters)
        data[i:i+n] = reading
        curve.setData(data)
        i = (i+n) % bufferSize
        line.setValue(i)
    except:
        print("could not convert to float") #catch if there is a failure to convert to float


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ START GETTING DATA FOREVER! ~~~~~~~~~~~~~~~~~~~~~~~~~~~~


timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(10)

#ser.close()
