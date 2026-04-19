from typing import List


class Reservation:
    def __init__(
        self,
        reservationID: str,
        partySize: int,
        status: str,
        createdAt: str,
        reservationType: str,
        date: str,
        startTime: str,
    ):
        self.reservationID = reservationID
        self.partySize = partySize
        self.status = status
        self.createdAt = createdAt
        self.reservationType = reservationType
        self.date = date
        self.startTime = startTime
        self.bookedTables: List[str] = []
        self.customerID: str = ""
        self.staffID: str = ""
