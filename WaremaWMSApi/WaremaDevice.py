import base64

from dataclasses import dataclass


class WaremaDevice:
    def __init__(self, hub, serialNumber, name, channel):
        self.hub = hub
        self.SN = serialNumber
        self.name = name
        self.channel = channel

        self.status = self.getStatus()

    def setStatus(self, setting0=255, setting1=255, setting2=255, setting3=255):
        self.hub.channelCommandRequest(self.channel, setting0, setting1, setting2, setting3)

    def getStatus(self) -> str:
        response = self.hub.mb8Read(block=1, adr=0, eui=self.SN, length=7)

        fields = base64.b64decode(response['data'])

        try:
            return (fields[0], fields[1], fields[2], fields[3])
        except KeyError as e:
            print(f"Failed to extract bytes from bytearray {fields} / sequenceLock: {response['sequenceLockActive']}")
            raise e

@dataclass
class VenetianBlindStatus:
    position: int
    tilt: int

    @classmethod
    def create(cls, position, tilt):
        return cls(position / 2, tilt - 127)

class VenetianBlind(WaremaDevice):
    def setPosition(self, position: int, tilt: int) -> None:
        self.setStatus(position * 2, tilt + 127)

    def getStatus(self):
        data = super().getStatus()

        return VenetianBlindStatus.create(data[0], data[1])


