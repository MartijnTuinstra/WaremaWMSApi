import json
import logging

from typing import Any, Optional


from .devices.baseDevice import BaseWaremaDevice
from .devices.SyncDevice import SyncGeneralBlind, SyncVenetianBlind
from .devices.AsyncDevices import AsyncGeneralBlind, AsyncVenetianBlind
from .Shrouding import decode, encode

LOGGER = logging.getLogger(__name__)


def genericPostMessage(action: str = "", parameters: Optional[dict] = None) -> str:
    data: dict[str, Any] = {"action": action}

    if parameters is not None:
        data['parameters'] = parameters

    data["changeIds"] = []

    return json.dumps(data)


class BaseHub:
    def __init__(self, web_address: str, ip_port: int = 80):
        if ip_port != 80:
            self.web_address: str = f"http://{web_address}:{ip_port}"
        else:
            self.web_address: str = f"http://{web_address}"

        self.devices: dict[int, BaseWaremaDevice] = {}
        self.status = {}

    def getDeviceFromSerialNumber(self, serialNumber: int) -> BaseWaremaDevice:
        return self.devices[serialNumber]

    def getDeviceFromIndex(self, index: int) -> BaseWaremaDevice:
        return list(self.devices.values())[index]

    def _processReceiverBlock(self, data: bytes, sync: bool = True) -> dict[int, BaseWaremaDevice]:
        for x in range(0, int(len(data) / 64)):
            device = data[x * 64:(x + 1) * 64]

            elementSerial = int.from_bytes(device[0:4], 'little')

            LOGGER.debug("".join(f"{y:02x}" for y in device))

            if elementSerial == 0:
                continue

            elementSerial = int.from_bytes(device[0:4], 'little')
            elementName = device[24:].decode().strip("\x00")

            LOGGER.debug("Found Device: %d / %s", elementSerial, elementName)

            if sync:
                if elementName.startswith("Raffstore"):
                    cls = SyncVenetianBlind
                else:
                    cls = SyncGeneralBlind
            else:
                if elementName.startswith("Raffstore"):
                    cls = AsyncVenetianBlind
                else:
                    cls = AsyncGeneralBlind

            self.devices[elementSerial] = cls(self, elementSerial, elementName, x)

        return self.devices

    @staticmethod
    def _channelCommandRequest(ch: int, fn: int, s0: int, s1: int, s2: int, s3: int) -> str:
        return genericPostMessage(
            action="channelCommandRequest",
            parameters={
                "channel": ch,
                "functionCode": fn,
                "setting0": s0,
                "setting1": s1,
                "setting2": s2,
                "setting3": s3
            }
        )

    @staticmethod
    def _manualCommandRequest(sn: int) -> str:
        return genericPostMessage(
            action="manualCommandRequest",
            parameters={
                "serialNumber": sn,
                "functionCode": 0
            }
        )

    @staticmethod
    def _mb8Read(block: int, adr: int, eui: int, length: int) -> str:
        return genericPostMessage(
            action="mb8Read",
            parameters={
                "address": adr,
                "block": block,
                "eui": eui,
                "length": length
            }
        )

    @staticmethod
    def _processResponse(response) -> dict[str, Any]:
        response = decode(response).decode()

        jsonresponse = json.loads(response)

        LOGGER.debug("Decoded response: %s", jsonresponse)

        if "response" in jsonresponse:
            return jsonresponse['response']

        return jsonresponse
