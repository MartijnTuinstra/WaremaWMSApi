from abc import ABC, abstractmethod
from typing import Optional


class BaseWaremaDevice(ABC):
    def __init__(self, hub, serialNumber, name, channel):
        self.hub = hub
        self.SN = serialNumber
        self.name = name
        self.channel = channel

    @abstractmethod
    def _setStatus(self, setting0=255, setting1=255, setting2=255, setting3=255):
        raise NotImplementedError('To be overridden!')

    @abstractmethod
    def _getStatus(self) -> tuple[int, ...]:
        raise NotImplementedError('To be overridden!')

    @abstractmethod
    def setPosition(self, **kwargs):
        raise NotImplementedError('To be overridden!')

    @abstractmethod
    def getPosition(self):
        raise NotImplementedError('To be overridden!')


class GeneralBlind(ABC):
    _minimum_position = 0
    _maximum_position = 100

    def _validPosition(self, position: Optional[int]) -> bool:
        if position is None:
            return False
        if not self._minimum_position <= position <= self._maximum_position:
            return False

        return True


class VenetianBlind(ABC):
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

    @abstractmethod
    def setTilt(self, tilt: int):
        raise NotImplementedError('To be overridden!')
