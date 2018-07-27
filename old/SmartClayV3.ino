#include <Arduino.h>
//#include "Wire.h"
//#include "I2Cdev.h"
//#include "MPU6050.h"

//IMU data
//MPU6050 accelgyro;
//int16_t ax, ay, az;

//xpn configure
int dig[8] = {2, 3, 4, 5, 6, 7, 8, 9}; //D2-D9
int i, j= 0;
int vSet[24] = {0};
int digConfig[8][8] = {
  {2, 0, 1, 0, 0, 1, 0, 1},
  {0, 2, 0, 1, 1, 0, 1, 0}, 
  {1, 0, 2, 0, 0, 1, 0, 1},
  {0, 1, 0, 2, 1, 0, 1, 0},
  {0, 1, 0, 1, 2, 0, 1, 0}, 
  {1, 0, 1, 0, 0, 2, 0, 1},
  {0, 1, 0, 1, 1, 0, 2, 0},
  {1, 0, 1, 0, 0, 1, 0, 2}
};

int inputPin[8][3] = {
  {0,2,7},
  {0,2,6},
  {0,3,6},
  {0,3,7},
  {1,2,7},
  {1,2,6},
  {1,3,6},
  {1,3,7}
};

int data[8][10];
int outputData[8];
int meanData[8];

void setup() {
  Serial.begin(115200);
  for(i=0;i!=8;i++){
    for(j=0;j!=10;j++){
      data[i][j] = 0;
    }
    outputData[i] = 0;
    meanData[i] = 0;
  }
  for (i = 0; i < 8; i++) {
    pinMode(dig[i], INPUT);
  }
}

void loop() {

  for (i = 0; i < 8; i++) {
    for (j = 0; j < 8; j++) {
      if (digConfig[i][j] == 0) {
        pinMode(dig[j], INPUT);
      }else if (digConfig[i][j] == 1) {
        pinMode(dig[j], OUTPUT);
        digitalWrite(dig[j], LOW);
      }else {
        pinMode(dig[j], OUTPUT);
        digitalWrite(dig[j], HIGH);
      }
    }
    delayMicroseconds(100);
    for(j=0;j!=3;j++){
      vSet[i*3+j] = analogRead(inputPin[i][j]);
    }
  }
  for(i=2;i!=9;i++){
    pinMode(i,INPUT);
  }
  for (i=0;i<8;i++){
    meanData[i] = 0;
    for(j=0;j!=9;j++){
      meanData[i]+=data[i][j+1];
      data[i][j] = data[i][j+1];
    }
    data[i][9] = vSet[i*3]+vSet[i*3+1]+vSet[i*3+2];
    meanData[i]+=data[i][9];
    meanData[i]/=10;
    outputData[i] = data[i][9] - meanData[i];
  }
  for (i = 0; i < 8; i++) {
    Serial.print(outputData[i]);
    Serial.print(" ");
  }
  Serial.write('\n');
  delay(20);
  /*Serial.print(ax);
  Serial.print(" ");
  Serial.print(ay);
  Serial.print(" ");
  Serial.println(az); */
}

