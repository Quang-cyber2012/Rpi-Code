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

buzzer = Buzzer(27)
buzzer.off()
button = Button(26,pull_up=True, hold_time=2)

drowsiness_alarm = False
obstacle_alarm = False
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
    "drowsiness_alarm": False,
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
    drowsiness_time = None
    obstacle_time = None
    buzzer_active = False
    buzzer_timeout = False
    buzzer_time = None
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
                    WriteLog(year, month, day, hour, minute, second, lat, lon, speed, drowsiness_alarm, roll, pitch, gyro)
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
                if is_closed or is_down or is_yawn:
                    if drowsiness_time is None:
                        drowsiness_time = time.monotonic()

                    if not drowsiness_alarm and time.monotonic() - drowsiness_time >= 5:
                        drowsiness_alarm = True
                        print("Buzzer On")
                else:
                    drowsiness_time = None
                    drowsiness_alarm = False
                if warning:
                    if obstacle_time is None:
                        obstacle_time = time.monotonic()

                    if not obstacle_alarm and time.monotonic() - obstacle_time >= 5:
                        obstacle_alarm = True
                else:
                    obstacle_time = None
                    obstacle_alarm = False
                if drowsiness_alarm or obstacle_alarm:
                    if not buzzer_active and not buzzer_timeout:
                        buzzer.on()
                        buzzer_active = True
                        buzzer_time = time.monotonic()
                    if (
                        buzzer_active
                        and buzzer_time is not None
                        and time.monotonic() - buzzer_time >= 10
                    ):
                        buzzer.off()
                        buzzer_active = False
                        buzzer_timeout = True

                        if drowsiness_alarm:
                            EventLog("Drowsy",year, month, day, hour, minute, second)
                        if obstacle_alarm:
                            EventLog("Obstacle",year, month, day, hour, minute, second)
                            buzzer_time = None
                else:
                    # Danger condition has completely disappeared
                    if buzzer_active:
                        buzzer.off()

                    buzzer_active = False
                    buzzer_timeout = False
                    buzzer_time = None

                    drowsiness_alarm = False
                    obstacle_alarm = False
                    drowsiness_time = None
                    obstacle_time = None
                with shared_data_lock:
                    shared_data.update({
                        "lat": lat,
                        "lon": lon,
                        "speed": speed,
                        "is_drowsy": drowsiness_alarm,
                        "pitch": pitch,
                        "roll": roll,
                        "gyro": gyro,
                        "time": f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}",
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
            ai_stop_event.set()
            break
if __name__ == "__main__":
    ai_thread = threading.Thread(
        target=ai_dect_loop,
        daemon=True
    )
    radar_worker = threading.Thread(
        target=radar_thread,
        daemon=True
    )
    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True
    )
    ai_thread.start()
    radar_worker.start()
    flask_thread.start()

    main()
