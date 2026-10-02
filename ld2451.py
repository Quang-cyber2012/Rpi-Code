import asyncio
import threading

from bleak import BleakClient
MAC = "25:1C:2C:FF:B5:8E"
FFF1 = "0000fff1-0000-1000-8000-00805f9b34fb"

distance = None
distance_lock = threading.Lock()

def notification_handler(sender, data):
    global distance

    if data[:4] != bytes.fromhex("f4 f3 f2 f1"):
        return

    if data[-4:] != bytes.fromhex("f8 f7 f6 f5"):
        return
    payload = data[4:-4]
    if len(payload) < 4:
        return
    target_count = payload[2]
    if target_count == 0:
        with distance_lock:
            distance = None
        return
    for target_index in range(target_count):
        distance_index = 5 + target_index * 5
        if distance_index >= len(payload):
            return
        new_distance = payload[distance_index]
        with distance_lock:
            distance = new_distance
        return
async def radar_loop():
    try:
        async with BleakClient(MAC) as client:
            print("Radar ready")

            await client.start_notify(
                FFF1,
                notification_handler
            )
            while True:
                await asyncio.sleep(0.01)
    except Exception as e:
        print("Radar not ready:", e)
def radar_thread():
    asyncio.run(radar_loop())
def LD2451read():
    with distance_lock:
        return distance

