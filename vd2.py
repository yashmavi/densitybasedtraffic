import cv2
import time
import imutils
from imutils.video import VideoStream
import serial
import argparse
print(cv2.__version__)



_CURRENT_GREEN   = "GREEN"
_CURRENT_RED     = "RED"
_CURRENT_YELLOW  = "YELLOW"

current_color   = None
current_side    = 0


_EXTRA_PER_CAR = 5

_GREEN_TIME = 5
_RED_TIME = 5
_YELLOW_TIME = 3


# print alailable serial ports list of computer
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()
for port, desc, hwid in sorted(ports):
        #print("{}: {} [{}]".format(port, desc, hwid))
        print("{}: {}".format(port, desc))






# argumnet parsing here
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--port", required=True,
    help = "com port of arduino")
ap.add_argument("-s", "--source", required=True,
    help = "source of video stream 0 default camera 1 webcam or video path")
args = vars(ap.parse_args())
port = args['port']
camera_number = int(args['source'])
port = port 
baud = 115200






#configuring serial communication port
serialPort = serial.Serial(port, baud, timeout=1)
# open the serial port
if serialPort.isOpen():
    print(serialPort.name + ' is open...')







# cascade classifier xml file
cascade_src = 'cars.xml'
#opening camera here
cap = cv2.VideoCapture(camera_number)
print("[INFO] camera sensor warming up...")
time.sleep(2.0)
#using opencv cascade classifier 
car_cascade = cv2.CascadeClassifier(cascade_src)



seconds = 0
seconds_last = 0
tick = False
last_update = 0



while True:
    ret, img = cap.read()
    if not ret:
        continue
   
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cars = car_cascade.detectMultiScale(gray, 1.1, 1)
    
    car_no = 0
    for (x,y,w,h) in cars:
        if w > 100 and h > 100 and  w < 200 and h < 200:
            car_no += 1
            #print(x,y,w,h)
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)      
    
    side1_extra_time = car_no*_EXTRA_PER_CAR
    
    # font 
    font = cv2.FONT_HERSHEY_SIMPLEX 
    # org 
    org = (50, 50) 
    # fontScale 
    fontScale = 1
    # Blue color in BGR 
    color = (255, 0, 0) 
    # Line thickness of 2 px 
    thickness = 2
    img = cv2.putText(img, str(car_no)+" seconds: "+str(seconds), org, font,  
                   fontScale, color, thickness, cv2.LINE_AA)
    cv2.imshow('Stream', img)
    
    
    
    
    
    seconds = int(time.perf_counter())
    
    
    if seconds_last != seconds:
        seconds_last = seconds
        tick = True
    
    
    
    if tick:
        tick = False
        print("tick: ",seconds)
        if current_color is None:
            current_color = _CURRENT_GREEN
            last_update = seconds
            current_side = 1
            print("SIDE 1 GREEN ","SIDE 2 RED   ")
            serialPort.write("GREEN1 RED2\n".encode('ascii'))
            
        
            
        if current_color ==  _CURRENT_GREEN and current_side == 1 and (last_update + _GREEN_TIME + side1_extra_time) < seconds:
            #CHANGE TO YELLOW
            current_color = _CURRENT_YELLOW
            last_update = seconds
            print("SIDE 1 YELLOW","SIDE 2 YELLOW")
            serialPort.write("YELLOW1 YELLOW2\n".encode('ascii'))
            
        
        if current_color ==  _CURRENT_YELLOW and current_side == 1 and last_update + _YELLOW_TIME < seconds:
            #CHANGE TO RED
            current_color = _CURRENT_RED
            last_update = seconds
            print("SIDE 1 RED   ","SIDE 2 GREEN ")
            serialPort.write("RED1 GREEN2\n".encode('ascii'))
            
            
        if current_color ==  _CURRENT_RED and current_side == 1 and last_update + _RED_TIME < seconds:
            #CHANGE TO YELLOW
            current_color = _CURRENT_YELLOW
            last_update = seconds
            current_side  = 2
            print("SIDE 1 YELLOW","SIDE 2 YELLOW")
            serialPort.write("YELLOW1 YELLOW2\n".encode('ascii'))
            
            
        if current_color ==  _CURRENT_YELLOW and current_side == 2 and last_update + _YELLOW_TIME < seconds:
            #CHANGE TO GREEN
            current_color = _CURRENT_GREEN
            last_update = seconds
            current_side = 1
            print("SIDE 1 GREEN ","SIDE 2 RED   ")
            serialPort.write("GREEN1 RED2\n".encode('ascii'))
                
                
            
            
        
        
        
         
           
        
    
    
    
    
    if cv2.waitKey(33) == 27:
        break

    
    



cv2.destroyAllWindows()