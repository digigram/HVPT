//Happy Vertical People Transporter
//http://hackaday.io/project/539-Happy-Vertical-People-Transporter

//Written by DigiGram - http://blog.digigram.za.net
//GPLv3 applies

//define pins
const int levelPin = 3;
const int motorPos = 4;
const int motorNeg = 5;

//define other variables
int currentFloor;
int currentFloorRes;
int DCP;
long rnd;
const int maxFloor = 2

void setup()
{
  Serial.begin(9600);
  pinMode(levelPin, INPUT);
  pinMode(motorPos, OUTPUT);
  pinMode(motorNeg, OUTPUT);
  randomSeed(5); //No real randomness is required
}

void floorDisplay(int floorNr, int destFloor = 1){
  int dispNr;
  dispNr = floorNr;
  //set a special display for some floors
  if (floorNr == 0) { dispNr = '8L';}
  if (floorNr == 13) { dispNr = '42';}
  if (floorNr == 37) { dispNr = '42';}
  if (floorNr == 42) { dispNr = '1337';}  
  
  //This will be sent back to Python to show on the cams
  String floorMsg = String(floorNr) + '/' + String(destFloor);
  Serial.write(floorMsg);
}

void gothere(int destFloor)
{
  int updown;
  
  //Control the H-bridge by feeding direction
  currentFloorRes = analogRead(levelPin);
  if (currentFloorRes > 640 && currentFloorRes < 735){
    currentFloor = 0;
  }
  else if (currentFloorRes > 735 && currentFloorRes < 830){
    currentFloor = 1;
  }
  else if (currentFloorRes > 830 && currentFloorRes < 900){
    currentFloor = 2;
  }
  else { currentFloor = 0;} 
  //if no connection to the level sensor, assume lift is in basement
  //as soon as it moves up a bit, it should make contact again and
  //get a good reading to act upon
  
  floorDisplay(currentFloor, destFloor);
  
  //up or down
  if (destFloor < currentFloor){
    updown = 'down';
  }
  if (destFloor > currentFloor){
    updown = 'up';
  }
  
  //now tell the HVPT
  if (updown == 'up'){
    analogWrite(motorPos, 500);
    digitalWrite(motorNeg, LOW);
    destFloor = destFloor +1; // To deal with the design flaw.
  }
  else if (updown == 'down'){
    analogWrite(motorNeg, 500);
    digitalWrite(motorPos, LOW);
  }    
  
  while (currentFloor != destFloor){
    currentFloorRes = analogRead(levelPin);
    if (currentFloorRes > 640 && currentFloorRes < 735){
      currentFloor = 0;
    }
    else if (currentFloorRes > 735 && currentFloorRes < 830){
      currentFloor = 1;
    }
    else if (currentFloorRes > 830 && currentFloorRes < 900){
      currentFloor = 2;
    }
    else { currentFloor = 0;}
    
    floorDisplay(currentFloor, destFloor);
  }

  
  digitalWrite(motorPos, LOW);
  digitalWrite(motorNeg, LOW);
  floorDisplay(currentFloor);
}

void loop()
{
  //DCP = feed from Defocussed Computer Perception
  DCP = Serial.read();
  currentFloorRes = analogRead(levelPin);
  if (currentFloorRes > 640 && currentFloorRes < 735){
      currentFloor = 0;
  }
  else if (currentFloorRes > 735 && currentFloorRes < 830){
    currentFloor = 1;
  }
  else if (currentFloorRes > 830 && currentFloorRes < 900){
    currentFloor = 2;
  }
  else { currentFloor = 0;}
    
  //floorDisplay(currentFloor, destFloor);  
  floorDisplay(currentFloor);
  
  if (DCP >= 0){
    gothere(DCP);
    delay(500);
    rnd = random(0,maxFloor+1);
    if (DCP != 0){
      gothere(rnd);
      //When the HPVT is in the basement, it needs some personal time
    }
  }
}

