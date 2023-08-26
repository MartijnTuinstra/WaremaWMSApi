# WaremaWMSApi
An api for controlling a Warema WMS system

Currently only a venetian blind is supported.

## Installation

```
$ python3 setup.py install
```

## Example Synchronize Usage

```
from WaremaWMSApi import SyncWaremaHub


# Create Hub
hub = SyncWaremaHub("webcontrol.home")
```
This will connect and load all devices.

The hub has a dictionary of all devices listed by serialnumber.
```
for dev in hub.devices.values():
    print(dev.name, dev.getPosition())
```

This will print the current status of each blind.
```
device.setPosition(10, 10)
```
Will extend the blind to 10% and rotate to 10 degrees.



## Example Asynchronize Usage

```
import asyncio

from WaremaWMSApi import AsyncWaremaHub


# creating a function to await the response
# for a single device and print status of each blind
async def position(device):
    print(device.name, await dev.getPosition())


async def main():
    # Create Hub using the context manager it will automaticly close the session.
    async with AsyncWaremaHub("192.168.1.12") as hub:
        # Check for intergrated devices
        devices = await hub.getDevices()
        # devices also accessable as hub.devices
        
        tasks: set[asyncio.Task] = set()

        # loop through the device list by creating tasks
        for dev in devices.values():
            tasks.add(asyncio.create_task(position(dev)))

        # wait for all requests
        await asyncio.gather(*tasks)

        # To set a blind position
        dev.setPosition(10, 10)


asyncio.run(main())

```