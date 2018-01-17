#Brent Turner - CSC 400 independent project - Arduino Oscilloscope
import sys
import glob
import serial
import io
import time
import numpy as np
import pyqtgraph as pg
import keyboard

def key(event):
    if event.char == event.keysym:
        msg = 'Normal Key %r' % event.char
    elif len(event.char) == 1:
        msg = 'Punctuation Key %r (%r)' % (event.keysym, event.char)
    else:
        msg = 'Special Key %r' % event.keysym
    label1.config(text=msg)

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
ser = serial.Serial(selectedPort, 9600,timeout=1, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GET THE GRAPH SETUP ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

try:    
    plt = pg.plot()
    #bufferSize = 10000
    bufferSize = 1000
    data = np.zeros(bufferSize)
    curve = plt.plot()
    line = plt.addLine(x=0)
    plt.setRange(xRange=[0, bufferSize], yRange=[-15, 15])
    i = 0
    xMin = 0;
    xMax = bufferSize;
except:
    print("Graph Config Error")

def update():
    global plt, xMax, xMin
    
    #This allows to scale the View Up
    if keyboard.is_pressed('RIGHT'):
        #print("Right Pressed")
        xMax = xMax + 10
        plt.setXRange(0, xMax)

    #This allows to scale the View Down
    if keyboard.is_pressed('LEFT') and xMax > 0:
        #print("Left Pressed")
        xMax = xMax - 10
        plt.setXRange(0, xMax)
        
    global data, curve, line, i

    n = 2  # update n samples per iteration
    
    try:        
        reading = float(ser.readline().strip()) * 3.06060606061 #The value my voltage divider works at (6.8k and 3.3k ohlm resisters)
        data[i:i+n] = reading
        curve.setData(data)
        i = (i+n) % bufferSize
        line.setValue(i)
    except:
        error = "error" #tired of letting the console get filled with blank serial posts
        #print("Could not convert to float") #catch if there is a failure to convert to float
        #print("/" +sio.readLine() + "/") #debug


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ START GETTING DATA FOREVER! ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start() #Give 0 Delay
