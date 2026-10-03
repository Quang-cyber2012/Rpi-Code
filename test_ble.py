import asyncio
from bleak import BleakScanner, BleakClient

MAC = "25:1C:2C:FF:B5:8E"
FFF1 = "0000fff1-0000-1000-8000-00805f9b34fb"


def notification_handler(sender, data):
    print("FFF1:", data.hex(" "))


async def main():
    device = await BleakScanner.find_device_by_address(MAC)

    if device is None:
        print("Radar not found")
        return

    async with BleakClient(device) as client:
        print("Connected:", client.is_connected)

        await client.start_notify(
            FFF1,
            notification_handler
        )

        print("Listening FFF1...")

        while True:
            await asyncio.sleep(0.1)


asyncio.run(main())
