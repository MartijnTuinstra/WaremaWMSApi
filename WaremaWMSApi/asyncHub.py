import aiohttp
import logging

from base64 import b64decode

from .devices.baseDevice import BaseWaremaDevice
from .Shrouding import encode
from .baseHub import BaseHub

LOGGER = logging.getLogger(__name__)


class AsyncWaremaHub(BaseHub):
    def __init__(self, web_address: str, ip_port: int = 80):
        super().__init__(web_address, ip_port)
        self.session = aiohttp.ClientSession(self.web_address)

    async def __aenter__(self) -> "AsyncWaremaHub":
        if self.session.closed:
            self.session = aiohttp.ClientSession(self.web_address)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close_session()

    async def close_session(self):
        await self.session.close()

    async def getHubInfo(self) -> dict:
        self.status = await self.request(path="info")
        return self.status

    async def channelCommandRequest(self, ch: int, fn: int, s0: int, s1: int, s2: int, s3: int) -> None:
        await self.post(
            self._channelCommandRequest(ch, fn, s0, s1, s2, s3)
        )

    async def manualCommandRequest(self, sn: int) -> dict:
        return await self.post(
            self._manualCommandRequest(sn)
        )

    async def mb8Read(self, block: int, adr: int, eui: int, length: int) -> dict:
        response = await self.post(
            self._mb8Read(block, adr, eui, length)
        )

        response['data'] = b64decode(response['data'])
        return response

    async def getDevices(self) -> dict[int, BaseWaremaDevice]:
        if not self.status:
            await self.getHubInfo()

        response = await self.mb8Read(block=42, adr=0, eui=int(self.status['serialNumber']), length=62 * 20)

        return self._processReceiverBlock(response['data'], False)

    async def getBlock(self, block, adr=0, length=188 * 10):
        # Block 42 Receiver list { blocks of 64 bytes }
        # Block 44 Room list { blocks of 84 bytes }
        # Block 48 -- Unknown { blocks of 188 bytes }
        # Block 50 Device name list { blocks of 188 bytes }
        # Block 81 -- Unknown
        return await self.mb8Read(block, adr, int(self.status['serialNumber']), length)

    async def request(self, path: str = "info") -> dict:
        LOGGER.debug("Get message from: %s/%s", self.web_address, path)

        async with self.session.get(f"/{path}", timeout=2) as r:
            await r.content.wait_eof()
            return self._processResponse(await r.content.readany())

    async def post(self, message: str = "", path: str = "postMessage", base64Data: bool = False) -> dict:
        LOGGER.debug("Post message to be send: %s", message)
        data = encode(message.encode("ascii"))

        async with self.session.post(f"/{path}", data=data, timeout=2) as r:
            await r.content.wait_eof()
            return self._processResponse(await r.content.readany())
