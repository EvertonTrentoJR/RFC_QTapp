#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_BNO08x.h>

Adafruit_BNO08x bno08x(-1);
sh2_SensorValue_t sensorValue;

struct ImuData
{
    float ax = 0, ay = 0, az = 0;
    float gx = 0, gy = 0, gz = 0;
    float mx = 0, my = 0, mz = 0;
    float qi = 0, qj = 0, qk = 0, qr = 1;
};

ImuData imu;

uint32_t lastPrint = 0;

void setup()
{
    Serial.begin(115200);
    delay(2000);

    Wire.begin();

    if (!bno08x.begin_I2C(0x4A, &Wire))
    {
        Serial.println("BNO085 not detected!");

        while (1)
        {
            delay(1000);
        }
    }

    Serial.println("BNO085 detected successfully!");

    // Report interval is in microseconds

    if (!bno08x.enableReport(SH2_ACCELEROMETER, 10000))
        Serial.println("Failed to enable accelerometer");

    if (!bno08x.enableReport(SH2_GYROSCOPE_CALIBRATED, 10000))
        Serial.println("Failed to enable gyroscope");

    if (!bno08x.enableReport(SH2_MAGNETIC_FIELD_CALIBRATED, 20000))
        Serial.println("Failed to enable magnetometer");

    if (!bno08x.enableReport(SH2_ROTATION_VECTOR, 10000))
        Serial.println("Failed to enable rotation vector");

    Serial.println(
        "Ax,Ay,Az,Gx,Gy,Gz,Mx,My,Mz,Qi,Qj,Qk,Qr"
    );
}

void loop()
{
    // Read all available BNO085 reports
    if (bno08x.getSensorEvent(&sensorValue))
    {
        switch (sensorValue.sensorId)
        {
            case SH2_ACCELEROMETER:

                imu.ax = sensorValue.un.accelerometer.x;
                imu.ay = sensorValue.un.accelerometer.y;
                imu.az = sensorValue.un.accelerometer.z;

                break;


            case SH2_GYROSCOPE_CALIBRATED:

                imu.gx = sensorValue.un.gyroscope.x;
                imu.gy = sensorValue.un.gyroscope.y;
                imu.gz = sensorValue.un.gyroscope.z;

                break;


            case SH2_MAGNETIC_FIELD_CALIBRATED:

                imu.mx = sensorValue.un.magneticField.x;
                imu.my = sensorValue.un.magneticField.y;
                imu.mz = sensorValue.un.magneticField.z;

                break;


            case SH2_ROTATION_VECTOR:

                imu.qi = sensorValue.un.rotationVector.i;
                imu.qj = sensorValue.un.rotationVector.j;
                imu.qk = sensorValue.un.rotationVector.k;
                imu.qr = sensorValue.un.rotationVector.real;

                break;
        }
    }


    // Send complete data stream at 50 Hz
    if (millis() - lastPrint >= 20)
    {
        lastPrint = millis();

        // Accelerometer
        Serial.print(imu.ax, 4);
        Serial.print(",");

        Serial.print(imu.ay, 4);
        Serial.print(",");

        Serial.print(imu.az, 4);
        Serial.print(",");

        // Gyroscope
        Serial.print(imu.gx, 4);
        Serial.print(",");

        Serial.print(imu.gy, 4);
        Serial.print(",");

        Serial.print(imu.gz, 4);
        Serial.print(",");

        // Magnetometer
        Serial.print(imu.mx, 3);
        Serial.print(",");

        Serial.print(imu.my, 3);
        Serial.print(",");

        Serial.print(imu.mz, 3);
        Serial.print(",");

        // Quaternion
        Serial.print(imu.qi, 5);
        Serial.print(",");

        Serial.print(imu.qj, 5);
        Serial.print(",");

        Serial.print(imu.qk, 5);
        Serial.print(",");

        Serial.println(imu.qr, 5);
    }
}