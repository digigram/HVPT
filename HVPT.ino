//Happy Vertical People Transporter
//http://hackaday.io/project/539-Happy-Vertical-People-Transporter

//Written by DigiGram - blog.digigram.za.net
//GPLv3 applies (for now - see README)

//define pins
const int levelPin = 3;
const int motorPos = 4;
const int motorNeg = 5;
const int seg0a = 6;
/*const int seg0b = 7;
const int seg1 = 8;
const int seg2 = 9;
const int seg3 = 10;
const int seg4 = 11;
const int seg5 = 12;
const int seg6 = 13;
const int seg7 = ??;*/

//define other variables
int currentFloor;
int currentFloorRes;
int DCP;
long rnd;
const int maxFloor = 42;
const int minFloor = 0;
const int minRes = 20;  //calibrate these values
const int maxRes = 500; //calibrate these values

void setup()
{
  Serial.begin(9600);
  pinMode(levelPin, INPUT);
  pinMode(motorPos, OUTPUT);
  pinMode(motorNeg, OUTPUT);
  randomSeed(5); //No real randomness is required
}

void floorDisplay(int floorNr){
  int dispNr;
  dispNr = floorNr;
  //set a special display for some floors
  if (floorNr == 0) { dispNr = '8L';}
  if (floorNr == 13) { dispNr = '42';}
  if (floorNr == 37) { dispNr = '42';}
  if (floorNr == 42) { dispNr = '1337';}  
  
  //print dispNr;  
}

void gothere(int destFloor)
{
  int updown;
  
  //Control the H-bridge by feeding the amount of floors and direction
  currentFloorRes = analogRead(levelPin);
  currentFloor = map(currentFloorRes, minRes, maxRes, minFloor, maxFloor);  
  floorDisplay(currentFloor);
  
  //up or down
  if (destFloor < currentFloor){
    updown = 'down';
  }
  if (destFloor > currentFloor){
    updown = 'up';
  }
  
  //now tell the HVPT
  if (updown == 'up'){
    analogWrite(motorPos, 500); //or something like this to make the motor go down slowly
    digitalWrite(motorNeg, LOW);
  }
  else if (updown == 'down'){
    analogWrite(motorNeg, 500); //or something like this to make the motor go down slowly
    digitalWrite(motorPos, LOW);
  }    
  
  while (currentFloor != destFloor){
    currentFloorRes = analogRead(levelPin);
    currentFloor = map(currentFloorRes, minRes, maxRes, minFloor, maxFloor);  
    floorDisplay(currentFloor);
  }
  digitalWrite(motorPos, LOW);
  digitalWrite(motorNeg, LOW);
}

void loop()
{
  
  //DCP = feed from Defocussed Computer Perception
  DCP = Serial.read();
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

