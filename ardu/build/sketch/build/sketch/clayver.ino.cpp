#line 1 "c:\\Users\\Liyf\\OneDrive\\Desktop\\Summer\\clayver\\proj\\ardu\\clayver.ino"
#line 1 "c:\\Users\\Liyf\\OneDrive\\Desktop\\Summer\\clayver\\proj\\ardu\\clayver.ino"
#include <Arduino.h>

const int SERIAL_RATE = 9600;
const int DELAY_TIME = 50;
const int ANA_NUM = 6;
const int DIG_NUM = 6;

const int ANA_PORTS[ANA_NUM] = {A0, A1, A2, A3, A4, A5};
const int DIG_PORTS[DIG_NUM] = {2, 3, 4, 5, 6, 7};

int signals[ANA_NUM] = {0};

#line 13 "c:\\Users\\Liyf\\OneDrive\\Desktop\\Summer\\clayver\\proj\\ardu\\clayver.ino"
void setup();
#line 21 "c:\\Users\\Liyf\\OneDrive\\Desktop\\Summer\\clayver\\proj\\ardu\\clayver.ino"
void loop();
#line 13 "c:\\Users\\Liyf\\OneDrive\\Desktop\\Summer\\clayver\\proj\\ardu\\clayver.ino"
void setup()
{
    for (int i = 0; i <DIG_NUM; i++) {
        pinMode(DIG_PORTS[i], OUTPUT);
    }
    Serial.begin(SERIAL_RATE);
}

void loop()
{
    for (int i = 0; i <DIG_NUM; i++) {
        digitalWrite(DIG_PORTS[i], HIGH);
    }
    String output;
    for (int i = 0; i < ANA_NUM; i++) {
        signals[i] = analogRead(ANA_PORTS[i]);
        output += String(signals[i]) + " ";
    }
    // output += String(signals[0]) + ' ' + String(signals[1]);

    Serial.println(output);
    delay(DELAY_TIME);
}

