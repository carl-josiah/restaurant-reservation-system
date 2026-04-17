class Notification:
    def __init__(self, notificationID: str, type: str, sentAt: str, message: str):
        self.notificationID = notificationID
        self.type = type
        self.sentAt = sentAt
        self.message = message
        self.customerID: str = ""  # The 'sent to' line
