import os

def WriteLog(year, month, day, hh, mm, ss, lat, lon, speed, is_sleeping, roll, pitch, gyro):
    folder = "/mnt/sdcard/logs/Normal Logs"
    os.makedirs(folder, exist_ok=True)

    filename = f"{year:04d}-{month:02d}-{day:02d}.log"
    path = os.path.join(folder, filename)

    is_sleeping = "Awake" if is_sleeping else "Asleep"
    gyro_str = f"{gyro[0]:.2f},{gyro[1]:.2f},{gyro[2]:.2f}" if gyro else "0,0,0"

    with open(path, "a", encoding="utf-8") as f:
        f.write(
            f"[{hh:02d}:{mm:02d}:{ss:02d}],"
            f"[{lat:.6f},{lon:.6f}, {speed:.2f}km/h],"
            f"[Driver status:{is_sleeping},Roll:{roll:.2f},Pitch:{pitch:.2f},Gyro:{gyro_str}]\n"
        )
def EventLog(event_type, year, month, day, hh, mm, ss):
    folder = "/mnt/sdcard/logs/Dangerous Events"
    os.makedirs(folder, exist_ok=True)

    filename = f"{year:04d}-{month:02d}-{day:02d}.log"
    path = os.path.join(folder, filename)

    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{hh:02d}:{mm:02d}:{ss:02d}],Event:{event_type}\n")