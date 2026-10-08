import time
from rtc import RTCread

for i in range(10):
    print("RTC:", RTCread())
    print("Pi :", time.localtime())
    print()
    time.sleep(1)
