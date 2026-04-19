import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import bcrypt
from unittest.mock import MagicMock
from src.logic.reservation_factory import ReservationFactory
from src.utils.constants import STATUS_CONFIRMED, STATUS_ACTIVE, TYPE_ONLINE, TYPE_WALKIN


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
