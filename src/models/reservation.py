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
    ):
        self.reservationID = reservationID
        self.partySize = partySize
        self.status = status
        self.createdAt = createdAt
        self.reservationType = reservationType
        self.date = date

        # Relationships from the lines in the diagram:
        self.bookedTables: List[str] = []  # The 1..* 'books' line
        self.customerID: str = ""  # The 'makes' line
        self.slotID: str = ""  # The 'scheduled for' line
        self.staffID: str = ""  # The 'manages' line
