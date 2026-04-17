from typing import List


class Table:
    def __init__(
        self,
        tableID: str,
        tableNumber: int,
        capacity: int,
        location: str,
        isActive: bool = True,
    ):
        self.tableID = tableID
        self.tableNumber = tableNumber
        self.capacity = capacity
        self.location = location
        self.isActive = isActive


class TimeSlot:
    def __init__(self, slotID: str, duration: int, startTime: str, endTime: str):
        self.slotID = slotID
        self.duration = duration
        self.startTime = startTime
        self.endTime = endTime
        self.reservations: List[str] = (
            []
        )  # handle the '0..*' relationship to reservation
