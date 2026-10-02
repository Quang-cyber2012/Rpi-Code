from i2c import i2c
import adafruit_mpu6050

ACCEL_OFFSET = (
    -0.7778856962,
    -0.1362779585,
    -1.7485716637
)

GYRO_OFFSET = (
    -0.0067526922,
    -0.0433305299,
    -0.0084266095
)

mpu = adafruit_mpu6050.MPU6050(i2c, address=0x69)


def MPUread():
    try:
        ax, ay, az = mpu.acceleration
        gx, gy, gz = mpu.gyro

        ax += ACCEL_OFFSET[0]
        ay += ACCEL_OFFSET[1]
        az += ACCEL_OFFSET[2]

        gx += GYRO_OFFSET[0]
        gy += GYRO_OFFSET[1]
        gz += GYRO_OFFSET[2]

        return (ax, ay, az), (gx, gy, gz)

    except Exception as e:
        print(f"MPU6050 Error: {e}")
        return None, None
print(MPUread())
