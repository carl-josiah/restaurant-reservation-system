class NotificationService:
    def __init__(self):
        self.gateway_ready = True

    def send_confirmation(self, reservation):
        if reservation.customerID:
            print(f"Confirmation sent for {reservation.reservationID}")

    def send_cancellation(self, reservation):
        if reservation.customerID:
            print(f"Cancellation notice sent for {reservation.reservationID}")
