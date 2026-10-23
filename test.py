
from gpiozero import Buzzer
from time import sleep

buzzer = Buzzer(27)

try:
    print("GPIO17: buzzer ON")
    buzzer.on()
    sleep(2)

    print("GPIO17: buzzer OFF")
    buzzer.off()
    sleep(2)

finally:
    buzzer.off()
    buzzer.close()
    print("Test finished")
