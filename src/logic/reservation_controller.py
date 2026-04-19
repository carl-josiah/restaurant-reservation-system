import re
from datetime import datetime

from src.persistence.storage_manager import StorageManager
from src.logic.reservation_factory import ReservationFactory
from src.logic.notification_service import NotificationService
from src.utils.error_handler import show_message, log_error
from src.utils.constants import (
    FLD_TABLE_ID,
    FLD_RES_ID,
    FLD_NAME,
    FLD_USER_ID,
    FLD_EMAIL,
    FLD_PASSWORD,
    FILE_RESERVATIONS,
    FILE_USERS,
    PREFIX_RES,
    PREFIX_USER,
    CAT_AUTH,
    CAT_SUCCESS,
    CAT_ERROR,
    TYPE_ONLINE,
    ROLE_CUSTOMER,
    STR_SIZE,
    PARTY_SIZE,
)


class BookingRequest:
    """Prevent code smell aka more than 3 paramaters"""

    def __init__(
        self, customer_id, table_ids, date, start_time, party_size, res_type=TYPE_ONLINE
    ):
        self.customer_id = customer_id
        self.table_ids = table_ids
        self.date = date
        self.start_time = start_time
        self.party_size = party_size
        self.res_type = res_type


class UserRegistration:
    """Prevent code smell aka more than 3 paramaters"""

    def __init__(self, name, email, password, phone, role=ROLE_CUSTOMER):
        self.name = name
        self.email = email
        self.password = password
        self.phone = phone
        self.role = role


class ReservationController:
    def __init__(self):
        self.storage = StorageManager()
        self.factory = ReservationFactory()
        self.notifications = NotificationService()
        self.current_user = None

    def _is_not_empty(self, data):
        if data is None:
            return False
        if isinstance(data, str):
            return len(data.strip()) > 0
        return True

    def _load_config_value(self, key, default):
        config = self.storage.load_config()
        if isinstance(config, dict):
            return config.get(key, default)
        return default

    def _get_table_by_id(self, table_id):
        tables = self.storage.load_tables()
        for table in tables:
            if table.get(FLD_TABLE_ID) == table_id:
                return table
        return None

    def _is_table_available(self, table_id, date, start_time):
        reservations = self.storage.load_reservations()
        for res in reservations:
            if table_id in res.get("bookedTables", []):
                if res.get("date") == date and res.get("startTime") == start_time:
                    return False
        return True

    def _is_table_valid_for_party(self, table_id, party_size):
        table = self._get_table_by_id(table_id)
        if not table or not table.get("isActive"):
            return False, f"Table {table_id} is not available."
        if table.get("capacity", 0) < party_size:
            return False, f"Table {table_id} cannot fit {party_size} guests."
        return True, None

    def _is_valid_name(self, name, max_len=STR_SIZE):
        if not isinstance(name, str):
            return False, "Name must be a string."
        name = name.strip()
        if not name:
            return False, "Name cannot be empty."
        if len(name) > max_len:
            return False, f"Name must be at most {max_len} characters."
        if not name.isalpha():
            return False, "Name must contain letters only."
        return True, None

    def _is_valid_email(self, email):
        if not isinstance(email, str):
            return False, "Email must be a string."
        email = email.strip()
        if not email:
            return False, "Email cannot be empty."
        if len(email) > 100:
            return False, "Email is too long."
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, email):
            return False, "Email format is invalid."
        return True, None

    def _is_valid_phone(self, phone):
        if not isinstance(phone, str):
            return False, "Phone must be a string."
        phone = phone.strip()
        if not phone:
            return False, "Phone cannot be empty."
        if not phone.isdigit():
            return False, "Phone must contain digits only."
        if len(phone) != 10:
            return False, "Phone must be exactly 10 digits."
        if not phone.startswith("05"):
            return False, "Phone must start with 05."
        return True, None

    def _is_valid_password(self, password, min_len=8, max_len=20):
        if not isinstance(password, str):
            return False, "Password must be a string."
        password = password.strip()
        if len(password) < min_len:
            return False, f"Password must be at least {min_len} characters."
        if len(password) > max_len:
            return False, f"Password must be at most {max_len} characters."
        if " " in password:
            return False, "Password cannot contain spaces."
        if not any(c.isupper() for c in password):
            return False, "Password must contain an uppercase letter."
        if not any(c.islower() for c in password):
            return False, "Password must contain a lowercase letter."
        if not any(c.isdigit() for c in password):
            return False, "Password must contain a number."
        if not any(not c.isalnum() for c in password):
            return False, "Password must contain a special character."
        return True, None

    def _is_valid_date(self, date_str):
        if not self._is_not_empty(date_str):
            return False, "Date cannot be empty."
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True, None
        except ValueError:
            return False, "Date must be in YYYY-MM-DD format."

    def _is_valid_time(self, time_str):
        if not self._is_not_empty(time_str):
            return False, "Start time cannot be empty."
        try:
            datetime.strptime(time_str, "%H:%M")
            return True, None
        except ValueError:
            return False, "Start time must be in HH:MM format."

    def _is_future_reservation(self, date_str, time_str):
        ok, reason = self._is_valid_date(date_str)
        if not ok:
            return False, reason
        ok, reason = self._is_valid_time(time_str)
        if not ok:
            return False, reason

        try:
            reservation_dt = datetime.strptime(
                f"{date_str} {time_str}", "%Y-%m-%d %H:%M"
            )
            if reservation_dt <= datetime.now():
                return False, "Reservation must be in the future."
            return True, None
        except ValueError:
            return False, "Reservation datetime is invalid."

    def _is_valid_party_size(self, size):
        max_party_size = self._load_config_value("maxPartySize", PARTY_SIZE)
        if not self._is_not_empty(size):
            return False, "Party size cannot be empty."
        try:
            val = int(size)
        except (ValueError, TypeError):
            return False, "Party size must be a number."
        if val < 1:
            return False, "Party size must be at least 1."
        if val > max_party_size:
            return False, f"Party size must be at most {max_party_size}."
        return True, None

    def _get_suitable_table(self, party_size, date, start_time):
        tables = self.storage.load_tables()
        for table in tables:
            if not table.get("isActive"):
                continue
            if table.get("capacity", 0) < party_size:
                continue
            table_id = table.get(FLD_TABLE_ID)
            if table_id and self._is_table_available(table_id, date, start_time):
                return table_id
        return None

    def login(self, email, password):
        users = self.storage._load_file(FILE_USERS)
        for u in users:
            if u.get(FLD_EMAIL) == email and u.get(FLD_PASSWORD) == password:
                self.current_user = u
                user_name = u.get(FLD_NAME, "User")
                show_message(f"Welcome back, {user_name}!", CAT_AUTH)
                return u
        log_error("Invalid email or password.", CAT_AUTH)
        return None

    def logout(self):
        if self.current_user:
            user_name = self.current_user.get(FLD_NAME, "User")
            self.current_user = None
            show_message(f"Goodbye, {user_name}! You have been logged out.", CAT_AUTH)
        else:
            log_error("No user is currently logged in.", CAT_AUTH)

    def make_reservation(self, request: BookingRequest):
        if not self.current_user:
            log_error("Reservation failed: No active session.", CAT_AUTH)
            return None

        ok, reason = self._is_future_reservation(request.date, request.start_time)
        if not ok:
            log_error(f"Reservation failed: {reason}", CAT_ERROR)
            return None

        ok, reason = self._is_valid_party_size(request.party_size)
        if not ok:
            log_error(f"Reservation failed: {reason}", CAT_ERROR)
            return None

        if not request.table_ids or len(request.table_ids) == 0:
            table_id = self._get_suitable_table(
                request.party_size, request.date, request.start_time
            )
            if not table_id:
                log_error("Reservation failed: No suitable table available.", CAT_ERROR)
                return None
            request.table_ids = [table_id]

        for table_id in request.table_ids:
            ok, reason = self._is_table_valid_for_party(table_id, request.party_size)
            if not ok:
                log_error(f"Reservation failed: {reason}", CAT_ERROR)
                return None

            if not self._is_table_available(table_id, request.date, request.start_time):
                log_error(
                    f"Reservation failed: Table {table_id} is already booked for this time.",
                    CAT_ERROR,
                )
                return None

        request.customer_id = self.current_user.get(FLD_USER_ID)
        res_id = self.storage.generate_next_id(
            FILE_RESERVATIONS, PREFIX_RES, FLD_RES_ID
        )
        new_res = self.factory.create_reservation(res_id, request)
        self.storage.save_reservations(vars(new_res))
        self.notifications.send_confirmation(new_res)
        show_message(f"Reservation {res_id} confirmed successfully!", CAT_SUCCESS)
        return new_res

    def register_user(self, reg_data: UserRegistration):
        checks = [
            (self._is_valid_name, reg_data.name, "Name"),
            (self._is_valid_email, reg_data.email, "Email"),
            (self._is_valid_phone, reg_data.phone, "Phone"),
            (self._is_valid_password, reg_data.password, "Password"),
        ]
        for validator, value, field in checks:
            ok, reason = validator(value)
            if not ok:
                log_error(f"Registration failed: {field}: {reason}", CAT_AUTH)
                return None
        users = self.storage._load_file(FILE_USERS)
        for u in users:
            if u.get(FLD_EMAIL) == reg_data.email:
                log_error(
                    f"Registration failed: Email {reg_data.email} is already registered.",
                    CAT_AUTH,
                )
                return None
        user_id = self.storage.generate_next_id(FILE_USERS, PREFIX_USER, FLD_USER_ID)
        new_user_data = vars(reg_data)
        new_user_data[FLD_USER_ID] = user_id
        users.append(new_user_data)
        self.storage._save_file(FILE_USERS, users)
        show_message(f"User {reg_data.name} registered with ID {user_id}", CAT_SUCCESS)
        return new_user_data
