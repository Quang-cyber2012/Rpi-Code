import serial
import pynmea2
ser = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)

lat, lon, speed,speed_sum,speed_count = None,None,0,0,0

def GPSread():
    global lat, lon, speed, speed_sum,speed_count
    try:
        line = ser.readline().decode("ascii", errors='ignore').strip()
        if line.startswith("$GPGGA") or line.startswith("$GNGGA"):
            msg = pynmea2.parse(line)
            if msg.latitude and msg.longitude:
                lat = msg.latitude
                lon = msg.longitude
        elif line.startswith("$GPRMC") or line.startswith("$GNRMC"):
            msg = pynmea2.parse(line)
            raw_speed = float(msg.spd_over_grnd or 0) * 1.852
            speed_sum += raw_speed
            speed_count += 1
            if speed_count == 10:
                speed = speed_sum / speed_count
                speed_sum = 0
                speed_count = 0
        return lat, lon, speed
    except pynmea2.ParseError as e:
        print(f"GPS Parse Error: {e}")
        return lat, lon, speed
