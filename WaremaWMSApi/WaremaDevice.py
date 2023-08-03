import base64

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


class WaremaDevice(ABC):
    def __init__(self, hub, serialNumber, name, channel):
        self.hub = hub
        self.SN = serialNumber
        self.name = name
        self.channel = channel

    def _setStatus(self, setting0=255, setting1=255, setting2=255, setting3=255):
        self.hub.channelCommandRequest(self.channel, setting0, setting1, setting2, setting3)

    def _getStatus(self) -> tuple[int, ...]:
        response = self.hub.mb8Read(block=1, adr=0, eui=self.SN, length=7)

        fields = base64.b64decode(response['data'])

        try:
            return (fields[0], fields[1], fields[2], fields[3])
        except KeyError as e:
            print(f"Failed to extract bytes from bytearray {fields} / sequenceLock: {response['sequenceLockActive']}")
            raise e
        
    @abstractmethod
    def setPosition(self, **kwargs):
        raise NotImplementedError('To be overridden!')

    @abstractmethod
    def getPosition(self):
        raise NotImplementedError('To be overridden!')


@dataclass
class VenetianBlindStatus:
    position: int
    tilt: int

    @classmethod
    def create(cls, position, tilt):
        return cls(position / 2, tilt - 127)


class VenetianBlind(WaremaDevice):
    _minimum_position = 0
    _minimum_tilt = 0
    _maximum_position = 100
    _maximum_tilt = 80

    def _validPosition(self, position: Optional[int]) -> bool:
        if position is None:
            return False
        if not self._minimum_position <= position <= self._maximum_position:
            return False
        
        return True

    def _validTilt(self, tilt: Optional[int]) -> bool:
        if tilt is None:
            return False
        elif not self._minimum_tilt <= tilt <= self._maximum_tilt:
            return False
        
        return True
    
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


