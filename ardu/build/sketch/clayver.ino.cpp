#line 1 "c:\\Users\\Liyf\\OneDrive\\Desktop\\Summer\\clayver\\proj\\clayver\\clayver.ino"
#line 1 "c:\\Users\\Liyf\\OneDrive\\Desktop\\Summer\\clayver\\proj\\clayver\\clayver.ino"
#include <MPU9250.h>

#include <Adafruit_BMP280.h>

#include <Arduino.h>

MPU9250 mpu = MPU9250();

const int SERIAL_RATE = 9600;
const int DELAY_TIME = 20;
const int ANA_NUM = 6;
const int DIG_NUM = 6;

const int ANA_PORTS[ANA_NUM] = {A0, A1, A2, A3, A6, A7};
const int DIG_PORTS[DIG_NUM] = {2, 3, 4, 5, 6, 7};

int signals[ANA_NUM] = {0};

#line 19 "c:\\Users\\Liyf\\OneDrive\\Desktop\\Summer\\clayver\\proj\\clayver\\clayver.ino"
void setup();
#line 30 "c:\\Users\\Liyf\\OneDrive\\Desktop\\Summer\\clayver\\proj\\clayver\\clayver.ino"
void loop();
#line 19 "c:\\Users\\Liyf\\OneDrive\\Desktop\\Summer\\clayver\\proj\\clayver\\clayver.ino"
void setup()
{
    for (int i = 0; i <DIG_NUM; i++) {
        pinMode(DIG_PORTS[i], OUTPUT);
    }
    Serial.begin(SERIAL_RATE);
    if (mpu.begin() != 0) {  
        Serial.println("Could not find a valid MPU9250 sensor, check wiring!");
    }
}

void loop()
{
    // set output voltage
    for (int i = 0; i <DIG_NUM; i++) {
        digitalWrite(DIG_PORTS[i], HIGH);
    }
    
    // set mpu
    mpu.set_accel_range(RANGE_4G);
    mpu.set_gyro_range(RANGE_GYRO_250);
    mpu.set_mag_scale(SCALE_14_BITS);
    mpu.set_mag_speed(MAG_8_Hz);

    // get mpu data
    mpu.get_accel();
    mpu.get_accel_g();
    mpu.get_gyro();
    
    // get adc data
    String output;
    for (int i = 0; i < ANA_NUM; i++) {
        signals[i] = analogRead(ANA_PORTS[i]);
        output += String(signals[i]) + " ";
    }
    // merge adc & mpu
    output += String(mpu.x) + " ";
    output += String(mpu.y) + " ";
    output += String(mpu.z) + " ";

    output += String(mpu.gx) + " ";
    output += String(mpu.gy) + " ";
    output += String(mpu.gz) + " ";

    if(!mpu.get_mag()){

        output += String(mpu.mx) + " ";
        output += String(mpu.my) + " ";
        output += String(mpu.mz) + " ";
    }
    Serial.println(output);
    delay(DELAY_TIME);
}

