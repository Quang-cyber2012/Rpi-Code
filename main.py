import math
import os
import time
import threading
import traceback

from flask import Flask, jsonify
from flask_socketio import SocketIO

from gps import GPSread
from mpu import MPUread
from rtc import RTCread
from Camera import CameraRead, PrepareFrame, CameraStop, Analyze_Frame
from gpiozero import Buzzer, Button
from sdcard import WriteLog, EventLog
from ld2451 import LD2451read,radar_thread

buzzer = Buzzer(17)
buzzer.off()
button = Button(26,pull_up=True, hold_time=2)

app = Flask(__name__)
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)
shared_data = {
    "lat": None,
    "lon": None,
    "speed": None,
    "is_closed": False,
    "pitch": 0.0,
    "roll": 0.0,
    "gyro": None,
    "time": None,
    "distance": None
}

shared_data_lock = threading.Lock()
ai_stop_event = threading.Event()

ai_state = {
    "is_closed": False,
    "is_down": False,
    "is_yawn": False
}

ai_state_lock = threading.Lock()

@app.route("/")
def home():
    return "Raspberry Pi Server Running"
@app.route("/RevData")
def send_data():
    with shared_data_lock:
        data_copy = shared_data.copy()

    return jsonify(data_copy)
def run_flask():
    print("Starting Flask + SocketIO server...")

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=False,
        allow_unsafe_werkzeug=True
    )
def PiOff():
    print("Button pressed. Shutting down...")
    buzzer.on()
    time.sleep(0.5)
    buzzer.off()
    ai_stop_event.set()
    print("Camera and AI stopped.")
    os.system("sudo poweroff")
def ai_dect_loop():
    print("Starting AI...")

    while not ai_stop_event.is_set():
        try:
            frame = CameraRead()
            frame = PrepareFrame(frame)

            result = Analyze_Frame(frame)
            print(
                f"[AI] "
                f"eye={result['eye']} "
                f"head={result['head']} "
                f"yawn={result['yawn']}"
            )
            with ai_state_lock:
                if result["eye"] is not None:
                    ai_state["is_closed"] = result["eye"]

                if result["head"] is not None:
                    ai_state["is_down"] = result["head"]

                if result["yawn"] is not None:
                    ai_state["is_yawn"] = result["yawn"]
        except Exception as e:
            if ai_stop_event.is_set():
                break
            print(f"AI error: {e}")
            traceback.print_exc()
            time.sleep(0.5)
    CameraStop()
    print("AI stopped.")
def main():
    while True:
        try:
                if button.is_pressed:
                    PiOff()
                lat, lon, speed = GPSread()
                accel, gyro = MPUread()
                year, month, day, hour, minute, second = RTCread()
                distance = LD2451read()
                with ai_state_lock:
                    is_closed = ai_state["is_closed"]
                    is_down = ai_state["is_down"]
                    is_yawn = ai_state["is_yawn"]
                if accel:
                    ax, ay, az = accel
                else:
                    ax, ay, az = (0.0, 0.0, 1.0)

                roll = round(
                    math.degrees(
                        math.atan2(ay, az)
                    ),
                    3
                )
                pitch = round(
                    math.degrees(
                        math.atan2(
                            -ax,
                            math.sqrt(ay ** 2 + az ** 2)
                        )
                    ),
                    3
                )

                if gyro:
                    gyro = (
                        round(gyro[0] * 180 / math.pi, 3),
                        round(gyro[1] * 180 / math.pi, 3),
                        round(gyro[2] * 180 / math.pi, 3)
                    )
                if minute % 15 == 0 and second == 0:
                    WriteLog(year, month, day, hour, minute, second, lat, lon, speed, False, roll, pitch, gyro)
                warning = False
                if distance is not None and speed is not None and speed > 0:
                    if speed <= 60 and distance <= 35:
                        warning = True
                    elif speed <= 80 and distance <= 55:
                        warning = True
                    elif speed <= 100 and distance <= 70:
                        warning = True
                    elif speed <= 120 and distance <= 100:
                        warning = True

                with shared_data_lock:
                    shared_data.update({
                        "lat": lat,
                        "lon": lon,
                        "speed": speed,
                        "is_sleep": warning,
                        "pitch": pitch,
                        "roll": roll,
                        "gyro": gyro,
                        "time": f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}",
                        "distance": distance
                    })
                    data_to_emit = shared_data.copy()
                try:
                    socketio.emit(
                        "data",
                        data_to_emit
                    )
                except Exception as e:
                    print(f"Error emitting data: {e}")
                    traceback.print_exc()
        except Exception as e:
                print(f"Error in main loop: {e}")
                traceback.print_exc()
                time.sleep(1)
        except KeyboardInterrupt:
            print("Keyboard interrupt received. Shutting down...")
if __name__ == "__main__":
    ai_thread = threading.Thread(
        target=ai_dect_loop,
        daemon=True
    )
    ai_thread.start()
    radar_worker = threading.Thread(
        target=radar_thread,
        daemon=True
    )

    radar_worker.start()
    main()
