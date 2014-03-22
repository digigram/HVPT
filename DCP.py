import cv2
import numpy as np
import time
from PIL import Image

##### 
# *1: Just for testing without an Arduino attached
nowL = '4'
goL = ''
initCount = 0 #### *1
#####

def average(arr):
    total = 0
    avg = 0
    for n in arr:
        total += n
    return total/len(arr)
    
def diffImg(img0, img1, img2):
  dif1 = cv2.absdiff(img2, img1)
  dif2 = cv2.absdiff(img1, img0)
  return cv2.bitwise_and(dif1, dif2)

def currentLevelElevator():
    #this will call the Arduino
    #lvls = serial.Serial.read()
    #read from Arduino: level currently on / level going to
    #3/1
    global nowL
    global goL
    lvls = nowL + '/' + goL #### see above *1
    #lvls = '1/2'
    currentLevel = lvls.split('/')[0]
    goingtoLevel = ''
    if len(lvls.split('/')[1]) > 0:
      goingtoLevel = lvls.split('/')[1]
    return currentLevel, goingtoLevel
    
#initialise
cam = [0]
camLevel = [0]
passenger = 0
allCam = []
camLevel=['1']

#find and attach all connected cameras
for camNr in range(0,5):
    print camNr
    iscam = cv2.VideoCapture(camNr)
    print iscam.isOpened()
    if iscam.isOpened():
        allCam.append(iscam)
        
       
#iterate over all cameras
#This only works for 1 cam for now. This should be inside the while loop
for camNR in range(0, len(allCam)):
    title = "Defocused Computer Perception - Level: " + str(camLevel[camNR])
    cv2.namedWindow(title, cv2.CV_WINDOW_AUTOSIZE)

    # Read three images first:
    img_prev = cv2.flip(cv2.cvtColor(allCam[camNR].read()[1], cv2.COLOR_RGB2GRAY), 1)
    img = cv2.flip(cv2.cvtColor(allCam[camNR].read()[1], cv2.COLOR_RGB2GRAY), 1)
    img_fut = cv2.flip(cv2.cvtColor(allCam[camNR].read()[1], cv2.COLOR_RGB2GRAY), 1)

    #It's called last100 but can be any size. It's dynamic
    sizeOfMotionHistory = 5
    last100 = []
    for i in range(0,sizeOfMotionHistory):
        last100.append(0)
    last10 = [0,0,0,0,0,0,0,0,0,0]
    x0 = 0
    y0 = 0
    motion = 'None'
 
    while True:
      dimg = diffImg(img_prev, img, img_fut)
      #print cv2.countNonZero(dimg) #to calibrate pThresh once-off
      pThresh = 150000
      mThresh = 50000
      
      if cv2.countNonZero(dimg) > pThresh:
        moments = cv2.moments(dimg, 0) 
        area = moments['m00'] 
        #print area #to calibrate mThresh once-off
        if(area > mThresh):  
            x = int(abs(moments['m10'] / area))
            y = int(abs(moments['m01'] / area))
            dist = np.sqrt((x-x0)**2+(y-y0)**2)
            last100 = last100[1:len(last100)]
            last100.append(dist)
            if last100[len(last100)-1]>last100[0]:
                motionPrev = motion
                motion = 'Coming'
            if last100[len(last100)-1]<last100[0]:
                motionPrev = motion
                motion = 'Going'
            #if abs(average(last5) - last5[4]) < 5:
            #    motionPrev = motion
            #    motion = 'None'    
            
            #if motionPrev != motion: If you want to tag all motion
            #I just want to tag incoming persons
            if motion == 'Coming':
                currLvl, goingLvl = currentLevelElevator()
                if (str(currLvl) != str(camLevel[camNR])) and (str(goingLvl) != str(camLevel[camNR])):
                  initCount += 1 # *1
                  if initCount > 10: # *1
                    
                    #print str(x)+';'+str(y)
                    passenger += 1
                    
                    global goL #### see above *1
                    goL = str(camLevel[camNR]) #### see above *1
                    
                    if (passenger < 42):
                        print str(camLevel[camNR]) #this becomes a serial.Serial.write()
                    elif (passenger == 42):
                        print str(0) 
                        #send the HVPT to the basement for councelling
                    if (passenger > 44):
                        passenger = 0
                        #the HVPT will go into councelling, so it needs time. 
                        #Customers will have to wait and chit chat...
             
            thresholdedImage = dimg
            grayscaleOriginal = img
            
            #Do you want the crosshair on a inverted thresholded image
            showimg = thresholdedImage 
            #or on the grayscale original?
            ##showimg = grayscaleOriginal
            
            #Here you can choose to have a croshair (2 line statements)    
            cv2.line(showimg, (x-10, y), (x+10, y), 255)
            cv2.line(showimg, (x, y-10), (x, y+10), 255)
            #Or a circle        
            ##cv2.circle(showimg, (x, y),20,255,5)
            
            #How you want to tag the motion
            text = 'Passenger: ' + motion
            if x < 0.5*len(dimg):
                xtext = x - 25
                ytext = y - 25
            else:
                xtext = x - 250
                ytext = y - 25
            cv2.putText(showimg, text, (xtext,ytext), cv2.FONT_HERSHEY_SIMPLEX, 1, 255) 
            ####Try to take it away when no motion is detected. it looks silly tagging an empty floor with "passenger"
        
        lvlname = 'Level ' + str(camLevel[camNR])
        cv2.putText(showimg, lvlname, (25,25), cv2.FONT_HERSHEY_SIMPLEX, 1, 255)   
        currLvl = 'Elevator: ' + str(currentLevelElevator()[0])
        cv2.putText(showimg, currLvl, (len(showimg)-35, 25),  cv2.FONT_HERSHEY_SIMPLEX, 1, 255)
        currLvl = 'Going to: ' + str(currentLevelElevator()[1])
        cv2.putText(showimg, currLvl, (len(showimg)-35, 60),  cv2.FONT_HERSHEY_SIMPLEX, 1, 255)        
        cv2.imshow( title, showimg )

      # Read next image
      img_prev = img
      img = img_fut
      img_fut = cv2.flip(cv2.cvtColor(allCam[camNR].read()[1], cv2.COLOR_RGB2GRAY), 1)

      key = cv2.waitKey(10)
      if key == 27:
        cv2.destroyWindow(title)
        break

    print "Goodbye"
