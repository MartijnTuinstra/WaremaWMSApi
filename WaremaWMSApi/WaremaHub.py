import requests
import json
import logging

from typing import Optional
from base64 import b64decode

from .WaremaDevice import WaremaDevice, VenetianBlind
from .Shrouding import decode, encode

log = logging.getLogger("Warema")
logData = logging.getLogger("Warema.Data")


def genericPostMessage(action: str="", parameters: Optional[dict]=None) -> str:
    data = {"action": action}

    if parameters is not None:
        data['parameters'] = parameters

    data["changeIds"] = []

    return json.dumps(data)


class WaremaHub:
    def __init__(self, ip_address: str, ip_port: int=80):
        self.ip: tuple[str, int] = (ip_address, ip_port)

        self.devices: dict[int, WaremaDevice] = {}

        self._getHubInfo()
        self._loadDevices()

    def _getHubInfo(self) -> dict:
        log.debug("getHubInfo")

        response = self.request(path="info")

        self.status = response

        return self.status

    def channelCommandRequest(self, ch: int, s0: int, s1: int, s2: int, s3: int) -> None:
        self.post(genericPostMessage(
            action="channelCommandRequest",
            parameters={"channel": ch,
                        "functionCode":3,
                        "setting0": s0,
                        "setting1": s1,
                        "setting2": s2,
                        "setting3": s3
                        }
        ))

    def manualCommandRequest(self, sn: int) -> dict:
        response = self.post(genericPostMessage(
            action="manualCommandRequest",
            parameters={"serialNumber": sn,
                        "functionCode":0
            }
        ))

        return response
    
    def mb8Read(self, block: int, adr: int, eui: int, length: int) -> dict:
        response = self.post(genericPostMessage(
            action="mb8Read",
            parameters={"address": adr,
                        "block": block,
                        "eui": eui,
                        "length": length
            }
        ))

        return response
    
    def getDeviceFromSerialNumber(self, serialNumber: int) -> WaremaDevice:
        return self.devices[serialNumber]
    
    def getDeviceFromIndex(self, index: int) -> WaremaDevice:
        return list(self.devices.values())[index]

    def _loadDevices(self) -> None:
        # Block 42 Receiver list { blocks of 64 bytes }
        # Block 44 Room list { blocks of 84 bytes }
        # Block 48 -- Unknown { blocks of 188 bytes }
        # Block 50 Device name list { blocks of 188 bytes }
        # Block 81 -- Unknown

        response = self.mb8Read(block=42, adr=0, eui=int(self.status['serialNumber']), length=62*20)

        decoded = b64decode(response['data'])

        for x in range(0, int(len(decoded)/64)):
            device = decoded[x*64:(x+1)*64]

            elementSerial = int.from_bytes(device[0:4], 'little')

            logData.debug("".join(f"{y:02x}" for y in device))

            if elementSerial == 0:
                continue

            elementSerial = int.from_bytes(device[0:4], 'little')
            elementName = device[24:].decode().strip("\x00")

            log.debug("Found Device: %d / %s", elementSerial, elementName)


            if elementName.startswith("Raffstore"):
                cls = VenetianBlind
            else:
                cls = WaremaDevice

            self.addDevice(cls, x, elementSerial, elementName)

        # return self.devices
    
    def addDevice(self, cls: WaremaDevice, index: int, serial: int, name: str) -> WaremaDevice:
        self.devices[serial] = cls(self, serial, name, index)

        return self.devices[serial]

    def request(self, message: str="", path: str="postMessage") -> dict:
        data = encode(message.encode("ascii"))

        r = requests.get(f"http://{self.ip[0]}:{self.ip[1]}/{path}", data=data, timeout=2)

        response = decode(r.content).decode()

        jsonresponse = json.loads(response)

        if "response" in jsonresponse:
            return jsonresponse['response']
        
        return jsonresponse

    
    def post(self, message: str="", path: str="postMessage") -> dict:
        data = encode(message.encode("ascii"))

        r = requests.post(f"http://{self.ip[0]}:{self.ip[1]}/{path}", data=data, timeout=2)

        response = decode(r.content).decode()

        jsonresponse = json.loads(response)

        if "response" in jsonresponse:
            return jsonresponse['response']
        
        return jsonresponse