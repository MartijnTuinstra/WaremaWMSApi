from dataclasses import dataclass


@dataclass
class GeneralBlindStatus:
    setting0: int
    setting1: int
    setting2: int
    setting3: int

    @classmethod
    def create(cls, setting0, setting1, setting2, setting3):
        return cls(setting0 / 2, setting1 - 127, setting2, setting3)


@dataclass
class VenetianBlindStatus:
    position: int
    tilt: int

    @classmethod
    def create(cls, position, tilt):
        return cls(position / 2, tilt - 127)
