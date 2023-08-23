import requests
import logging

from base64 import b64decode

from .devices.baseDevice import BaseWaremaDevice
from .Shrouding import encode
from .baseHub import BaseHub

LOGGER = logging.getLogger(__name__)


class SyncWaremaHub(BaseHub):
    def __init__(self, web_address: str, ip_port: int = 80):
        super().__init__(web_address, ip_port)

        self.getHubInfo()
        self.getDevices()

    def getHubInfo(self) -> dict:
        self.status = self.request(path="info")
        return self.status

    def channelCommandRequest(self, ch: int, fn: int, s0: int, s1: int, s2: int, s3: int) -> None:
        self.post(
            self._channelCommandRequest(ch, fn, s0, s1, s2, s3)
        )

    def manualCommandRequest(self, sn: int) -> dict:
        return self.post(
            self._manualCommandRequest(sn)
        )

    def mb8Read(self, block: int, adr: int, eui: int, length: int) -> dict:
        response = self.post(
            self._mb8Read(block, adr, eui, length)
        )

        response['data'] = b64decode(response['data'])
        return response

    def getDevices(self) -> dict[int, BaseWaremaDevice]:
        response = self.mb8Read(block=42, adr=0, eui=int(self.status['serialNumber']), length=62 * 20)

        return self._processReceiverBlock(response['data'])

    def getBlock(self, block, adr=0, length=188 * 10):
        # Block 42 Receiver list { blocks of 64 bytes }
        # Block 44 Room list { blocks of 84 bytes }
        # Block 48 -- Unknown { blocks of 188 bytes }
        # Block 50 Device name list { blocks of 188 bytes }
        # Block 81 -- Unknown
        return self.mb8Read(block, adr, int(self.status['serialNumber']), length)

    def request(self, path: str = "info") -> dict:
        LOGGER.debug("Get message from: %s/%s", self.web_address, path)

        r = requests.get(f"{self.web_address}/{path}", timeout=2)

        return self._processResponse(r.content)

    def post(self, message: str = "", path: str = "postMessage") -> dict:
        LOGGER.debug("Post message to be send: %s", message)
        data = encode(message.encode("ascii"))

        r = requests.post(f"{self.web_address}/{path}", data=data, timeout=2)

        return self._processResponse(r.content)
