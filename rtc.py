import time
from i2c import i2c
import adafruit_ds3231

rtc = adafruit_ds3231.DS3231(i2c)


def RTCread():
    try:
        now = rtc.datetime

        return (
            now.tm_year,
            now.tm_mon,
            now.tm_mday,
            now.tm_hour,
            now.tm_min,
            now.tm_sec
        )
    except Exception as e:
        print(f"RTC Error: {e}")
        return None, None, None, None, None, None
if __name__ == "__main__":
   print(RTCread())
   time.sleep(5)
   print(RTCread())
   time.sleep(5)
   print(RTCread())
   time.sleep(5)
   print(RTCread())
   time.sleep(5)
   print(RTCread())
