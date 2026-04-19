class NotificationService:
    def __init__(self):
        self.gateway_ready = True

    def send_confirmation(self, reservation):
        if reservation.customerID:
            print(f"Confirmation sent for {reservation.reservationID}")

    def send_cancellation(self, reservation):
        customer_id = reservation.get("customerID") if isinstance(reservation, dict) else reservation.customerID
        res_id = reservation.get("reservationID") if isinstance(reservation, dict) else reservation.reservationID
        if customer_id:
            print(f"Cancellation notice sent for {res_id}")
