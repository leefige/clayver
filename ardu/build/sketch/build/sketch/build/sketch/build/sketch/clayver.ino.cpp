#line 1 "c:\\Users\\Liyf\\OneDrive\\Desktop\\Summer\\clayver\\proj\\ardu\\clayver.ino"
#line 1 "c:\\Users\\Liyf\\OneDrive\\Desktop\\Summer\\clayver\\proj\\ardu\\clayver.ino"
#include <Arduino.h>

const int SERIAL_RATE = 9600;
const int DELAY_TIME = 50;
const int PORT_NUM = 6;
const int VCC_PORT = 2;
const int ANA_PORTS[PORT_NUM] = {A0, A1, A2, A3, A4, A5};

int signals[PORT_NUM] = {0};

void setup()
{
    Serial.begin(SERIAL_RATE);
}

void loop()
{
    String output;
    for (int i = 0; i < PORT_NUM; i++) {
        signals[i] = analogRead(ANA_PORTS[i]);
        output += String(signals[i]) + " ";
    }
    // output += String(signals[0]) + ' ' + String(signals[1]);

    Serial.println(output);
    delay(DELAY_TIME);
}

