# WaremaWMSApi
An api for controlling a Warema WMS system

Currently only a venetian blind is supported.

## Installation

```
$ python3 setup.py install
```

## Example Use

```
# Create Hub
hub = SyncWaremaHub("webcontrol.home")
```
This will connect and load all devices.

The hub has a dictionary of all devices listed by serialnumber.
```
for dev in hub.devices.values():
    print(dev.name, dev.getStatus())
```

This will print the current status of each blind.
```
device.setStatus(10, 10)
```
Will extend the blind to 10% and rotate to 10 degrees.
