import datetime
from src.models.reservation import Reservation


class ReservationFactory:
    @staticmethod
    def create_reservation(res_id, request):
        status = "Confirmed" if request.res_type == "Online" else "Active"
        new_res = Reservation(
            reservationID=res_id,
            partySize=request.party_size,
            status=status,
            createdAt=datetime.datetime.now().isoformat(),
            reservationType=request.res_type,
            date=request.date,
        )
        new_res.bookedTables = request.table_ids
        new_res.slotID = request.slot_id
        return new_res
