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
