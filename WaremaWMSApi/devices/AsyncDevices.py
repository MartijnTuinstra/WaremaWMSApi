import base64

from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional

from .baseDevice import BaseWaremaDevice, GeneralBlind, VenetianBlind
from .blindStatus import GeneralBlindStatus, VenetianBlindStatus


class AsyncWaremaDevice(BaseWaremaDevice):
    async def _setStatus(self, setting0=255, setting1=255, setting2=255, setting3=255):
        await self.hub.channelCommandRequest(self.channel, setting0, setting1, setting2, setting3)

    async def _getStatus(self) -> tuple[int, ...]:
        response = await self.hub.mb8Read(block=1, adr=0, eui=self.SN, length=7)

        fields = response['data']

        try:
            return (fields[0], fields[1], fields[2], fields[3])
        except KeyError as e:
            print(f"Failed to extract bytes from bytearray {fields} / sequenceLock: {response['sequenceLockActive']}")
            raise e


class AsyncGeneralBlind(AsyncWaremaDevice, GeneralBlind):
    async def setPosition(self, position: int) -> None:
        if self._validPosition(position):
            position *= 2
        else:
            raise ValueError(f'Given position should be between {self._minimum_position} and {self._maximum_position}')

        await self._setStatus(position)

    async def getPosition(self) -> GeneralBlindStatus:
        data = await self._getStatus()

        return GeneralBlindStatus.create(*data)


class AsyncVenetianBlind(AsyncWaremaDevice, VenetianBlind):
    async def setTilt(self, tilt: int):
        if self._validTilt(tilt):
            tilt += 127
        else:
            raise ValueError(f'Given tilt should be between {self._minimum_tilt} and {self._maximum_tilt}')

        await self._setStatus(setting1=tilt)

    async def setPosition(self, position: int, tilt: int = 255) -> None:
        if self._validPosition(position):
            position *= 2
        else:
            raise ValueError(f'Given position should be between {self._minimum_position} and {self._maximum_position}')

        if self._validTilt(tilt):
            tilt += 127
        else:
            tilt = 255

        await self._setStatus(position, tilt)

    async def getPosition(self) -> VenetianBlindStatus:
        data = await self._getStatus()

        return VenetianBlindStatus.create(data[0], data[1])
