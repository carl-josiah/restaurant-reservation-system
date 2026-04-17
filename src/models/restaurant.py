class Restaurant:
    def __init__(
        self,
        restaurantID: str,
        name: str,
        address: str,
        phoneNumber: str,
        openingHours: str,
        closingTime: str,
    ):
        self.restaurantID = restaurantID
        self.name = name
        self.address = address
        self.phoneNumber = phoneNumber
        self.openingHours = openingHours
        self.closingTime = closingTime
