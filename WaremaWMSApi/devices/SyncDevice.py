import base64

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from .baseDevice import BaseWaremaDevice, GeneralBlind, VenetianBlind
from .blindStatus import GeneralBlindStatus, VenetianBlindStatus


class SyncWaremaDevice(BaseWaremaDevice):
    def _setStatus(self, setting0=255, setting1=255, setting2=255, setting3=255):
        self.hub.channelCommandRequest(self.channel, setting0, setting1, setting2, setting3)

    def _getStatus(self) -> tuple[int, ...]:
        response = self.hub.mb8Read(block=1, adr=0, eui=self.SN, length=7)

        fields = response['data']

        try:
            return (fields[0], fields[1], fields[2], fields[3])
        except KeyError as e:
            print(f"Failed to extract bytes from bytearray {fields} / sequenceLock: {response['sequenceLockActive']}")
            raise e


class SyncGeneralBlind(SyncWaremaDevice, GeneralBlind):
    async def setPosition(self, position: int) -> None:
        if self._validPosition(position):
            position *= 2
        else:
            raise ValueError(f'Given position should be between {self._minimum_position} and {self._maximum_position}')

        self._setStatus(position)

    async def getPosition(self) -> GeneralBlindStatus:
        data = self._getStatus()

        return GeneralBlindStatus.create(*data)


class SyncVenetianBlind(SyncWaremaDevice, VenetianBlind):
    def setTilt(self, tilt: int):
        if self._validTilt(tilt):
            tilt += 127
        else:
            raise ValueError(f'Given tilt should be between {self._minimum_tilt} and {self._maximum_tilt}')

        self._setStatus(setting1=tilt)

    def setPosition(self, position: int, tilt: int = 255) -> None:
        if self._validPosition(position):
            position *= 2
        else:
            raise ValueError(f'Given position should be between {self._minimum_position} and {self._maximum_position}')

        if self._validTilt(tilt):
            tilt += 127
        else:
            tilt = 255

        self._setStatus(position, tilt)

    def getPosition(self) -> VenetianBlindStatus:
        data = self._getStatus()

        return VenetianBlindStatus.create(data[0], data[1])
