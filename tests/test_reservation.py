import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import bcrypt
from unittest.mock import MagicMock, patch
from src.logic.reservation_factory import ReservationFactory
from src.logic.reservation_controller import ReservationController
from src.utils.constants import (
    STATUS_CONFIRMED,
    STATUS_ACTIVE,
    STATUS_COMPLETED,
    TYPE_ONLINE,
    TYPE_WALKIN,
    FILE_RESERVATIONS,
)


def _make_controller(current_user):
    ReservationController._instance = None
    controller = ReservationController()
    controller.storage = MagicMock()
    controller.notifications = MagicMock()
    controller.current_user = current_user
    return controller


def test_factory_online_reservation_status():
    request = MagicMock()
    request.res_type = TYPE_ONLINE
    request.party_size = 2
    request.date = "2027-01-01"
    request.start_time = "18:00"
    request.table_ids = ["TBL-1"]
    request.customer_id = "USR-1"

    res = ReservationFactory.create_reservation("RES-1", request)
    assert res.status == STATUS_CONFIRMED


def test_factory_walkin_reservation_status():
    request = MagicMock()
    request.res_type = TYPE_WALKIN
    request.party_size = 3
    request.date = "2027-01-01"
    request.start_time = "12:00"
    request.table_ids = ["TBL-3"]
    request.customer_id = "USR-4"

    res = ReservationFactory.create_reservation("RES-2", request)
    assert res.status == STATUS_ACTIVE


def test_bcrypt_roundtrip():
    password = "TestPass@1"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")
    assert bcrypt.checkpw(password.encode(), hashed.encode())
    assert not bcrypt.checkpw(b"WrongPass@1", hashed.encode())


def test_status_transition_seat_guests():
    staff_user = {"id": "USR-4", "role": "Staff", "staffRole": "Regular", "name": "Khalid"}
    controller = _make_controller(staff_user)

    fake_res = {
        "reservationID": "RES-T1",
        "status": STATUS_CONFIRMED,
        "customerID": "USR-1",
        "date": "2027-06-01",
        "startTime": "18:00",
        "partySize": 2,
        "bookedTables": ["TBL-1"],
    }
    controller.storage.load_reservations.return_value = [fake_res]

    result = controller.seat_guests("RES-T1")

    assert result is not None
    assert result["status"] == STATUS_ACTIVE
    controller.storage._save_file.assert_called_once_with(FILE_RESERVATIONS, [fake_res])


def test_status_transition_complete():
    staff_user = {"id": "USR-4", "role": "Staff", "staffRole": "Regular", "name": "Khalid"}
    controller = _make_controller(staff_user)

    fake_res = {
        "reservationID": "RES-T2",
        "status": STATUS_ACTIVE,
        "customerID": "USR-1",
        "date": "2027-06-01",
        "startTime": "18:00",
        "partySize": 2,
        "bookedTables": ["TBL-1"],
    }
    controller.storage.load_reservations.return_value = [fake_res]

    result = controller.complete_reservation("RES-T2")

    assert result is not None
    assert result["status"] == STATUS_COMPLETED
    controller.storage._save_file.assert_called_once_with(FILE_RESERVATIONS, [fake_res])


def test_modify_reservation_updates_fields():
    customer_user = {"id": "USR-1", "role": "Customer", "name": "Layla"}
    controller = _make_controller(customer_user)

    fake_res = {
        "reservationID": "RES-T3",
        "status": STATUS_CONFIRMED,
        "customerID": "USR-1",
        "date": "2027-06-01",
        "startTime": "18:00",
        "partySize": 2,
        "bookedTables": ["TBL-1"],
    }
    controller.storage.load_reservations.return_value = [fake_res]
    controller.storage.load_tables.return_value = [
        {"tableID": "TBL-2", "tableNumber": 2, "capacity": 4, "location": "Indoor", "isActive": True}
    ]
    controller.storage.load_config.return_value = {"maxPartySize": 20}

    result = controller.modify_reservation("RES-T3", "2027-08-15", "19:00", 3)

    assert result is not None
    assert result["date"] == "2027-08-15"
    assert result["startTime"] == "19:00"
    assert result["partySize"] == 3
    assert result["bookedTables"] == ["TBL-2"]


def test_browse_availability_returns_list():
    customer_user = {"id": "USR-1", "role": "Customer", "name": "Layla"}
    controller = _make_controller(customer_user)

    controller.storage.load_tables.return_value = [
        {"tableID": "TBL-1", "tableNumber": 1, "capacity": 2, "location": "Indoor", "isActive": True},
        {"tableID": "TBL-2", "tableNumber": 2, "capacity": 4, "location": "Outdoor", "isActive": True},
        {"tableID": "TBL-3", "tableNumber": 3, "capacity": 1, "location": "Indoor", "isActive": True},
    ]
    controller.storage.load_reservations.return_value = []
    controller.storage.load_config.return_value = {"maxPartySize": 20}

    result = controller.browse_availability("2027-09-01", "20:00", 2)

    assert isinstance(result, list)
    assert len(result) == 2
    ids = [t["tableID"] for t in result]
    assert "TBL-1" in ids
    assert "TBL-2" in ids
    assert "TBL-3" not in ids
