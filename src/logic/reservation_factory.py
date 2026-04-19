import datetime
from src.utils.constants import STATUS_CONFIRMED, STATUS_ACTIVE, TYPE_ONLINE
from src.models.reservation import Reservation


class ReservationFactory:
    @staticmethod
    def create_reservation(res_id, request):
        status = STATUS_CONFIRMED if request.res_type == TYPE_ONLINE else STATUS_ACTIVE
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
