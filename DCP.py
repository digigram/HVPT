import cv2
import numpy
import time
from PIL import Image


def diffImg(t0, t1, t2):
  d1 = cv2.absdiff(t2, t1)
  d2 = cv2.absdiff(t1, t0)
  return cv2.bitwise_and(d1, d2)

sent = [0]
cam = [0]
camLevel = [0]
passenger = 0
sent[0] = time.time()
#cam = []
#for camNr in [2,1,0]:
#    cam.append(cv2.VideoCapture(camNr))
#print cam
#for camNr in [2,1,0]:
#    if (cam[camNr].isOpened() != True):
#        del cam[camNr]
        
#all that needs is to cycle cameras and do this for all cameras connected
#thus a sent[] also     
camNR = 0
cam[camNR] = cv2.VideoCapture(0)
camLevel[camNR] = 1

title = "Defocused Computer Perception"
cv2.namedWindow(title, cv2.CV_WINDOW_AUTOSIZE)

# Read three images first:
t_minus = cv2.cvtColor(cam[camNR].read()[1], cv2.COLOR_RGB2GRAY)
t = cv2.cvtColor(cam[camNR].read()[1], cv2.COLOR_RGB2GRAY)
t_plus = cv2.cvtColor(cam[camNR].read()[1], cv2.COLOR_RGB2GRAY)

while True:
  dimg = diffImg(t_minus, t, t_plus)
  #print cv2.countNonZero(dimg) #to calibrate pThresh once-off
  pThresh = 140000
  mThresh = 30000
  
  if cv2.countNonZero(dimg) > pThresh:
    moments = cv2.moments(dimg, 0) 
    area = moments['m00'] 
    #print area #to calibrate mThresh once-off
    if(area > mThresh):  
        x = int(abs(moments['m10'] / area))
        y = int(abs(moments['m01'] / area))
        if (time.time()-sent[camNR] > 10): 
            print str(x)+';'+str(y)
            sent[camNR] = time.time()
            passenger += 1
            if (passenger < 42):
                print str(camLevel[camNR]) #this becomes a serial.Serial.write()
            elif (passenger == 42):
                print str(0) 
                #send the HVPT to the basement for councelling
            if (passenger > 44):
                passenger = 0
                #the HVPT will go into councelling, so it needs time. 
                #Customers will have to wait and chit chat...
         
        #Do you want the crosshair on a inverted thresholded image
        ##showimg = dimg 
        #or on the grayscale original?
        showimg = t
        #Here you can choose to have a croshair (2 line statements)    
        cv2.line(showimg, (x-10, y), (x+10, y), 255)
        cv2.line(showimg, (x, y-10), (x, y+10), 255)
        #Or a circle    
        ##cv2.circle(showimg, (x, y),20,255,5)
        
    cv2.imshow( title, showimg )

  # Read next image
  t_minus = t
  t = t_plus
  t_plus = cv2.cvtColor(cam[camNR].read()[1], cv2.COLOR_RGB2GRAY)

  key = cv2.waitKey(10)
  if key == 27:
    cv2.destroyWindow(title)
    break

print "Goodbye"
