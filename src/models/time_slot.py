from typing import List


class TimeSlot:
    def __init__(self, slotID: str, duration: int, startTime: str, endTime: str):
        self.slotID = slotID
        self.duration = duration
        self.startTime = startTime
        self.endTime = endTime
        self.reservations: List[str] = []
