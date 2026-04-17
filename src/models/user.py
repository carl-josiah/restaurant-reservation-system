class User:
    """base class btw: inheritance and abstraction"""

    def __init__(self, userID: str, name: str, email: str, password: str):
        self.userID = userID
        self.name = name
        self.email = email
        self.password = password


class Customer(User):
    def __init__(
        self, customerID: str, name: str, email: str, password: str, phoneNumber: str
    ):
        super().__init__(customerID, name, email, password)
        self.phoneNumber = phoneNumber


class Staff(User):
    def __init__(self, staffID: str, name: str, email: str, password: str, role: str):
        super().__init__(staffID, name, email, password)
        self.role = role
