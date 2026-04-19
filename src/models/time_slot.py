"""
NOTE: TimeSlot is part of the design model (see Section 14 of the report). The current prototype
simplifies time handling by storing startTime as a string directly on Reservation. TimeSlot is
retained as a separate class for future expansion.
"""

from typing import List


class TimeSlot:
    def __init__(self, slotID: str, duration: int, startTime: str, endTime: str):
        self.slotID = slotID
        self.duration = duration
        self.startTime = startTime
        self.endTime = endTime
        self.reservations: List[str] = []
