import re
import bcrypt
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
    FLD_CUST_ID,
    FILE_RESERVATIONS,
    FILE_USERS,
    FILE_TABLES,
    FILE_CONFIG,
    PREFIX_RES,
    PREFIX_USER,
    PREFIX_TABLE,
    CAT_AUTH,
    CAT_SUCCESS,
    CAT_ERROR,
    TYPE_ONLINE,
    TYPE_WALKIN,
    ROLE_CUSTOMER,
    ROLE_STAFF,
    ROLE_ADMIN,
    STATUS_CONFIRMED,
    STATUS_ACTIVE,
    STATUS_CANCELLED,
    STATUS_COMPLETED,
    STATUS_NO_SHOW,
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
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self.storage = StorageManager()
        self.factory = ReservationFactory()
        self.notifications = NotificationService()
        self.current_user = None
        self._initialized = True

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

    def _is_table_available(self, table_id, date, start_time, exclude_res_id=None):
        reservations = self.storage.load_reservations()
        for res in reservations:
            if exclude_res_id and res.get(FLD_RES_ID) == exclude_res_id:
                continue
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

    def _get_suitable_table(self, party_size, date, start_time, exclude_res_id=None):
        tables = self.storage.load_tables()
        for table in tables:
            if not table.get("isActive"):
                continue
            if table.get("capacity", 0) < party_size:
                continue
            table_id = table.get(FLD_TABLE_ID)
            if table_id and self._is_table_available(table_id, date, start_time, exclude_res_id):
                return table_id
        return None

    def _is_staff(self):
        return self.current_user and self.current_user.get("role") == ROLE_STAFF

    def _is_admin(self):
        return self._is_staff() and self.current_user.get("staffRole") == ROLE_ADMIN

    def login(self, email, password):
        users = self.storage._load_file(FILE_USERS)
        for u in users:
            if u.get(FLD_EMAIL) == email:
                stored_hash = u.get(FLD_PASSWORD, "")
                if bcrypt.checkpw(password.encode(), stored_hash.encode()):
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
        hashed = bcrypt.hashpw(reg_data.password.encode(), bcrypt.gensalt()).decode("utf-8")
        new_user_data = vars(reg_data)
        new_user_data[FLD_PASSWORD] = hashed
        new_user_data[FLD_USER_ID] = user_id
        users.append(new_user_data)
        self.storage._save_file(FILE_USERS, users)
        show_message(f"User {reg_data.name} registered with ID {user_id}", CAT_SUCCESS)
        return new_user_data

    def cancel_reservation(self, reservation_id):
        if not self.current_user:
            log_error("Not logged in.", CAT_AUTH)
            return None
        reservations = self.storage.load_reservations()
        target = None
        for res in reservations:
            if res.get(FLD_RES_ID) == reservation_id:
                target = res
                break
        if not target:
            log_error(f"Reservation {reservation_id} not found.", CAT_ERROR)
            return None
        user_role = self.current_user.get("role")
        if user_role != ROLE_STAFF:
            if target.get(FLD_CUST_ID) != self.current_user.get(FLD_USER_ID):
                log_error("You can only cancel your own reservations.", CAT_ERROR)
                return None
        if target.get("status") != STATUS_CONFIRMED:
            log_error("Only confirmed reservations can be cancelled.", CAT_ERROR)
            return None
        target["status"] = STATUS_CANCELLED
        self.storage._save_file(FILE_RESERVATIONS, reservations)
        if target.get(FLD_CUST_ID):
            self.notifications.send_cancellation(target)
        show_message(f"Reservation {reservation_id} has been cancelled.", CAT_SUCCESS)
        return target

    def view_reservation_history(self):
        if not self.current_user:
            log_error("Not logged in.", CAT_AUTH)
            return None
        reservations = self.storage.load_reservations()
        user_id = self.current_user.get(FLD_USER_ID)
        history = [r for r in reservations if r.get(FLD_CUST_ID) == user_id]
        history.sort(key=lambda r: r.get("date", ""), reverse=True)
        return history

    def create_walkin_reservation(self, table_ids, party_size):
        if not self.current_user:
            log_error("Not logged in.", CAT_AUTH)
            return None
        if self.current_user.get("role") != ROLE_STAFF:
            log_error("Only staff can create walk-in reservations.", CAT_ERROR)
            return None
        ok, reason = self._is_valid_party_size(party_size)
        if not ok:
            log_error(f"Reservation failed: {reason}", CAT_ERROR)
            return None
        today = datetime.now().strftime("%Y-%m-%d")
        now_time = datetime.now().strftime("%H:%M")
        if not table_ids or len(table_ids) == 0:
            table_id = self._get_suitable_table(party_size, today, now_time)
            if not table_id:
                log_error("No suitable table available.", CAT_ERROR)
                return None
            table_ids = [table_id]
        for table_id in table_ids:
            ok, reason = self._is_table_valid_for_party(table_id, party_size)
            if not ok:
                log_error(f"Reservation failed: {reason}", CAT_ERROR)
                return None
        request = BookingRequest(
            customer_id=self.current_user.get(FLD_USER_ID),
            table_ids=table_ids,
            date=today,
            start_time=now_time,
            party_size=party_size,
            res_type=TYPE_WALKIN,
        )
        res_id = self.storage.generate_next_id(FILE_RESERVATIONS, PREFIX_RES, FLD_RES_ID)
        new_res = self.factory.create_reservation(res_id, request)
        self.storage.save_reservations(vars(new_res))
        show_message(f"Walk-in reservation {res_id} created successfully!", CAT_SUCCESS)
        return new_res

    def _find_reservation(self, reservation_id):
        reservations = self.storage.load_reservations()
        for res in reservations:
            if res.get(FLD_RES_ID) == reservation_id:
                return res, reservations
        return None, None

    def seat_guests(self, reservation_id):
        if not self.current_user:
            log_error("Not logged in.", CAT_AUTH)
            return None
        if not self._is_staff():
            log_error("Only staff can seat guests.", CAT_ERROR)
            return None
        target, reservations = self._find_reservation(reservation_id)
        if not target:
            log_error(f"Reservation {reservation_id} not found.", CAT_ERROR)
            return None
        if target.get("status") != STATUS_CONFIRMED:
            log_error("Only confirmed reservations can be seated.", CAT_ERROR)
            return None
        target["status"] = STATUS_ACTIVE
        self.storage._save_file(FILE_RESERVATIONS, reservations)
        show_message(f"Reservation {reservation_id} is now Active.", CAT_SUCCESS)
        return target

    def complete_reservation(self, reservation_id):
        if not self.current_user:
            log_error("Not logged in.", CAT_AUTH)
            return None
        if not self._is_staff():
            log_error("Only staff can complete reservations.", CAT_ERROR)
            return None
        target, reservations = self._find_reservation(reservation_id)
        if not target:
            log_error(f"Reservation {reservation_id} not found.", CAT_ERROR)
            return None
        if target.get("status") != STATUS_ACTIVE:
            log_error("Only active reservations can be completed.", CAT_ERROR)
            return None
        target["status"] = STATUS_COMPLETED
        self.storage._save_file(FILE_RESERVATIONS, reservations)
        show_message(f"Reservation {reservation_id} marked as Completed.", CAT_SUCCESS)
        return target

    def mark_no_show(self, reservation_id):
        if not self.current_user:
            log_error("Not logged in.", CAT_AUTH)
            return None
        if not self._is_staff():
            log_error("Only staff can mark no-shows.", CAT_ERROR)
            return None
        target, reservations = self._find_reservation(reservation_id)
        if not target:
            log_error(f"Reservation {reservation_id} not found.", CAT_ERROR)
            return None
        if target.get("status") != STATUS_CONFIRMED:
            log_error("Only confirmed reservations can be marked as no-show.", CAT_ERROR)
            return None
        grace_minutes = self._load_config_value("graceMinutes", 15)
        try:
            res_dt = datetime.strptime(
                f"{target.get('date')} {target.get('startTime')}", "%Y-%m-%d %H:%M"
            )
        except ValueError:
            log_error("Reservation has an invalid date or time.", CAT_ERROR)
            return None
        from datetime import timedelta
        if datetime.now() < res_dt + timedelta(minutes=grace_minutes):
            log_error("Grace period has not elapsed yet.", CAT_ERROR)
            return None
        target["status"] = STATUS_NO_SHOW
        self.storage._save_file(FILE_RESERVATIONS, reservations)
        show_message(f"Reservation {reservation_id} marked as No-show.", CAT_SUCCESS)
        return target

    def modify_reservation(self, reservation_id, new_date, new_start_time, new_party_size):
        if not self.current_user:
            log_error("Not logged in.", CAT_AUTH)
            return None
        target, reservations = self._find_reservation(reservation_id)
        if not target:
            log_error(f"Reservation {reservation_id} not found.", CAT_ERROR)
            return None
        if self.current_user.get("role") != ROLE_STAFF:
            if target.get(FLD_CUST_ID) != self.current_user.get(FLD_USER_ID):
                log_error("You can only modify your own reservations.", CAT_ERROR)
                return None
        if target.get("status") != STATUS_CONFIRMED:
            log_error("Only confirmed reservations can be modified.", CAT_ERROR)
            return None
        ok, reason = self._is_future_reservation(new_date, new_start_time)
        if not ok:
            log_error(f"Modification failed: {reason}", CAT_ERROR)
            return None
        ok, reason = self._is_valid_party_size(new_party_size)
        if not ok:
            log_error(f"Modification failed: {reason}", CAT_ERROR)
            return None
        new_table_id = self._get_suitable_table(
            int(new_party_size), new_date, new_start_time, exclude_res_id=reservation_id
        )
        if not new_table_id:
            log_error("Modification failed: No suitable table available for the new time.", CAT_ERROR)
            return None
        target["date"] = new_date
        target["startTime"] = new_start_time
        target["partySize"] = int(new_party_size)
        target["bookedTables"] = [new_table_id]
        self.storage._save_file(FILE_RESERVATIONS, reservations)
        if target.get(FLD_CUST_ID):
            self.notifications.send_confirmation(target)
        show_message(f"Reservation {reservation_id} updated successfully.", CAT_SUCCESS)
        return target

    def browse_availability(self, date, start_time, party_size):
        if not self.current_user:
            log_error("Not logged in.", CAT_AUTH)
            return None
        ok, reason = self._is_future_reservation(date, start_time)
        if not ok:
            log_error(f"Availability check failed: {reason}", CAT_ERROR)
            return None
        ok, reason = self._is_valid_party_size(party_size)
        if not ok:
            log_error(f"Availability check failed: {reason}", CAT_ERROR)
            return None
        tables = self.storage.load_tables()
        available = []
        for table in tables:
            if not table.get("isActive"):
                continue
            if table.get("capacity", 0) < int(party_size):
                continue
            table_id = table.get(FLD_TABLE_ID)
            if table_id and self._is_table_available(table_id, date, start_time):
                available.append({
                    FLD_TABLE_ID: table_id,
                    "tableNumber": table.get("tableNumber"),
                    "capacity": table.get("capacity"),
                    "location": table.get("location"),
                })
        return available

    def add_table(self, table_number, capacity, location):
        if not self.current_user:
            log_error("Not logged in.", CAT_AUTH)
            return None
        if not self._is_admin():
            log_error("Only admins can add tables.", CAT_ERROR)
            return None
        tables = self.storage.load_tables()
        for t in tables:
            if t.get("tableNumber") == table_number:
                log_error(f"Table number {table_number} already exists.", CAT_ERROR)
                return None
        table_id = self.storage.generate_next_id(FILE_TABLES, PREFIX_TABLE, FLD_TABLE_ID)
        new_table = {
            FLD_TABLE_ID: table_id,
            "tableNumber": table_number,
            "capacity": capacity,
            "location": location,
            "isActive": True,
        }
        tables.append(new_table)
        self.storage.save_tables(tables)
        show_message(f"Table {table_id} added successfully.", CAT_SUCCESS)
        return new_table

    def deactivate_table(self, table_id):
        if not self.current_user:
            log_error("Not logged in.", CAT_AUTH)
            return None
        if not self._is_admin():
            log_error("Only admins can deactivate tables.", CAT_ERROR)
            return None
        tables = self.storage.load_tables()
        target = None
        for t in tables:
            if t.get(FLD_TABLE_ID) == table_id:
                target = t
                break
        if not target:
            log_error(f"Table {table_id} not found.", CAT_ERROR)
            return None
        today = datetime.now().strftime("%Y-%m-%d")
        reservations = self.storage.load_reservations()
        upcoming = [
            r for r in reservations
            if table_id in r.get("bookedTables", [])
            and r.get("status") == STATUS_CONFIRMED
            and r.get("date", "") >= today
        ]
        if upcoming:
            show_message(
                f"Warning: {len(upcoming)} upcoming confirmed reservation(s) reference this table.",
                CAT_SUCCESS,
            )
        target["isActive"] = False
        self.storage.save_tables(tables)
        show_message(f"Table {table_id} deactivated.", CAT_SUCCESS)
        return target

    def reactivate_table(self, table_id):
        if not self.current_user:
            log_error("Not logged in.", CAT_AUTH)
            return None
        if not self._is_admin():
            log_error("Only admins can reactivate tables.", CAT_ERROR)
            return None
        tables = self.storage.load_tables()
        target = None
        for t in tables:
            if t.get(FLD_TABLE_ID) == table_id:
                target = t
                break
        if not target:
            log_error(f"Table {table_id} not found.", CAT_ERROR)
            return None
        target["isActive"] = True
        self.storage.save_tables(tables)
        show_message(f"Table {table_id} reactivated.", CAT_SUCCESS)
        return target

    def list_all_tables(self):
        if not self.current_user:
            log_error("Not logged in.", CAT_AUTH)
            return None
        return self.storage.load_tables()

    def update_config(self, key, value):
        if not self.current_user:
            log_error("Not logged in.", CAT_AUTH)
            return None
        if not self._is_admin():
            log_error("Only admins can update configuration.", CAT_ERROR)
            return None
        allowed_keys = {"maxPartySize", "graceMinutes", "minNoticeMinutes", "timeSlotMinutes"}
        if key not in allowed_keys:
            log_error(f"Invalid config key. Allowed: {', '.join(sorted(allowed_keys))}", CAT_ERROR)
            return None
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            log_error("Config value must be a positive integer.", CAT_ERROR)
            return None
        if int_value < 1:
            log_error("Config value must be a positive integer.", CAT_ERROR)
            return None
        config = self.storage.load_config()
        if not isinstance(config, dict):
            config = {}
        config[key] = int_value
        self.storage.save_config(config)
        admin_id = self.current_user.get(FLD_USER_ID)
        show_message(f"Config updated: {key}={int_value} by {admin_id} at {datetime.now().isoformat()}", CAT_SUCCESS)
        return config

    def get_config(self):
        if not self.current_user:
            log_error("Not logged in.", CAT_AUTH)
            return None
        if not self._is_staff():
            log_error("Only staff can view configuration.", CAT_ERROR)
            return None
        return self.storage.load_config()
