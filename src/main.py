import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.logic.reservation_controller import (
    ReservationController,
    UserRegistration,
    BookingRequest,
)
from src.utils.constants import (
    CAT_ERROR,
    FLD_NAME,
    TYPE_ONLINE,
    ROLE_STAFF,
    ROLE_ADMIN,
)
from src.utils.error_handler import log_error


def display_header():
    print("\n" + "=" * 45)
    print("      RESTAURANT RESERVATION SYSTEM")
    print("=" * 45)


def _print_reservation(res):
    print(
        f"  {res.get('reservationID')} | {res.get('date')} {res.get('startTime')} | "
        f"Party: {res.get('partySize')} | Status: {res.get('status')}"
    )


def _get_int(prompt):
    try:
        return int(input(prompt))
    except ValueError:
        return None


def _customer_menu(controller):
    print("1. Make a Reservation")
    print("2. Browse Available Tables")
    print("3. View My Reservations")
    print("4. Modify a Reservation")
    print("5. Cancel a Reservation")
    print("6. Logout")
    print("7. Exit Program")
    choice = input("\nSelect an option: ")

    if choice == "1":
        print("\n--- New Reservation ---")
        reservation_date = input("Enter Date (YYYY-MM-DD): ")
        start_time = input("Enter Start Time (HH:MM): ")
        party_size = _get_int("Enter Party Size: ")
        if party_size is None:
            log_error("Party size must be a number.", CAT_ERROR)
            return False
        request = BookingRequest(
            customer_id=None,
            table_ids=[],
            date=reservation_date.strip(),
            start_time=start_time.strip(),
            party_size=party_size,
            res_type=TYPE_ONLINE,
        )
        controller.make_reservation(request)

    elif choice == "2":
        print("\n--- Browse Available Tables ---")
        date = input("Enter Date (YYYY-MM-DD): ")
        start_time = input("Enter Start Time (HH:MM): ")
        party_size = _get_int("Enter Party Size: ")
        if party_size is None:
            log_error("Party size must be a number.", CAT_ERROR)
            return False
        tables = controller.browse_availability(date.strip(), start_time.strip(), party_size)
        if tables is None:
            return False
        if not tables:
            print("No tables available for the selected criteria.")
        else:
            print(f"\n  {'ID':<8} {'No.':<6} {'Capacity':<10} {'Location'}")
            for t in tables:
                print(f"  {t.get('tableID'):<8} {t.get('tableNumber'):<6} {t.get('capacity'):<10} {t.get('location')}")

    elif choice == "3":
        print("\n--- My Reservations ---")
        history = controller.view_reservation_history()
        if not history:
            print("No reservations found.")
        else:
            for res in history:
                _print_reservation(res)

    elif choice == "4":
        print("\n--- Modify Reservation ---")
        reservation_id = input("Enter Reservation ID: ").strip()
        new_date = input("Enter New Date (YYYY-MM-DD): ").strip()
        new_time = input("Enter New Start Time (HH:MM): ").strip()
        new_size = _get_int("Enter New Party Size: ")
        if new_size is None:
            log_error("Party size must be a number.", CAT_ERROR)
            return False
        controller.modify_reservation(reservation_id, new_date, new_time, new_size)

    elif choice == "5":
        print("\n--- Cancel Reservation ---")
        reservation_id = input("Enter Reservation ID: ")
        controller.cancel_reservation(reservation_id.strip())

    elif choice == "6":
        controller.logout()

    elif choice == "7":
        return True

    else:
        log_error("Invalid option selected.", CAT_ERROR)

    return False


def _staff_menu(controller):
    from datetime import datetime
    print("1. Create Walk-in Reservation")
    print("2. View Today's Reservations")
    print("3. Seat Guests (mark Active)")
    print("4. Complete Reservation")
    print("5. Mark as No-Show")
    print("6. Cancel Reservation")
    print("7. Logout")
    print("8. Exit Program")
    choice = input("\nSelect an option: ")

    if choice == "1":
        print("\n--- Walk-in Reservation ---")
        party_size = _get_int("Enter Party Size: ")
        if party_size is None:
            log_error("Party size must be a number.", CAT_ERROR)
            return False
        controller.create_walkin_reservation([], party_size)

    elif choice == "2":
        print("\n--- Today's Reservations ---")
        today = datetime.now().strftime("%Y-%m-%d")
        all_res = controller.storage.load_reservations()
        todays = [r for r in all_res if r.get("date") == today]
        if not todays:
            print("No reservations for today.")
        else:
            for res in todays:
                _print_reservation(res)

    elif choice == "3":
        print("\n--- Seat Guests ---")
        reservation_id = input("Enter Reservation ID: ").strip()
        controller.seat_guests(reservation_id)

    elif choice == "4":
        print("\n--- Complete Reservation ---")
        reservation_id = input("Enter Reservation ID: ").strip()
        controller.complete_reservation(reservation_id)

    elif choice == "5":
        print("\n--- Mark as No-Show ---")
        reservation_id = input("Enter Reservation ID: ").strip()
        controller.mark_no_show(reservation_id)

    elif choice == "6":
        print("\n--- Cancel Reservation ---")
        reservation_id = input("Enter Reservation ID: ").strip()
        controller.cancel_reservation(reservation_id)

    elif choice == "7":
        controller.logout()

    elif choice == "8":
        return True

    else:
        log_error("Invalid option selected.", CAT_ERROR)

    return False


def _admin_menu(controller):
    from datetime import datetime
    print("1.  Create Walk-in Reservation")
    print("2.  View Today's Reservations")
    print("3.  Seat Guests (mark Active)")
    print("4.  Complete Reservation")
    print("5.  Mark as No-Show")
    print("6.  Cancel Reservation")
    print("7.  Add Table")
    print("8.  Deactivate Table")
    print("9.  Reactivate Table")
    print("10. List All Tables")
    print("11. Update System Configuration")
    print("12. View Configuration")
    print("13. Logout")
    print("14. Exit Program")
    choice = input("\nSelect an option: ")

    if choice == "1":
        print("\n--- Walk-in Reservation ---")
        party_size = _get_int("Enter Party Size: ")
        if party_size is None:
            log_error("Party size must be a number.", CAT_ERROR)
            return False
        controller.create_walkin_reservation([], party_size)

    elif choice == "2":
        print("\n--- Today's Reservations ---")
        today = datetime.now().strftime("%Y-%m-%d")
        all_res = controller.storage.load_reservations()
        todays = [r for r in all_res if r.get("date") == today]
        if not todays:
            print("No reservations for today.")
        else:
            for res in todays:
                _print_reservation(res)

    elif choice == "3":
        print("\n--- Seat Guests ---")
        reservation_id = input("Enter Reservation ID: ").strip()
        controller.seat_guests(reservation_id)

    elif choice == "4":
        print("\n--- Complete Reservation ---")
        reservation_id = input("Enter Reservation ID: ").strip()
        controller.complete_reservation(reservation_id)

    elif choice == "5":
        print("\n--- Mark as No-Show ---")
        reservation_id = input("Enter Reservation ID: ").strip()
        controller.mark_no_show(reservation_id)

    elif choice == "6":
        print("\n--- Cancel Reservation ---")
        reservation_id = input("Enter Reservation ID: ").strip()
        controller.cancel_reservation(reservation_id)

    elif choice == "7":
        print("\n--- Add Table ---")
        table_number = _get_int("Enter Table Number: ")
        if table_number is None:
            log_error("Table number must be a number.", CAT_ERROR)
            return False
        capacity = _get_int("Enter Capacity: ")
        if capacity is None:
            log_error("Capacity must be a number.", CAT_ERROR)
            return False
        location = input("Enter Location (Indoor/Outdoor): ").strip()
        controller.add_table(table_number, capacity, location)

    elif choice == "8":
        print("\n--- Deactivate Table ---")
        table_id = input("Enter Table ID: ").strip()
        controller.deactivate_table(table_id)

    elif choice == "9":
        print("\n--- Reactivate Table ---")
        table_id = input("Enter Table ID: ").strip()
        controller.reactivate_table(table_id)

    elif choice == "10":
        print("\n--- All Tables ---")
        tables = controller.list_all_tables()
        if not tables:
            print("No tables found.")
        else:
            print(f"  {'ID':<8} {'No.':<6} {'Capacity':<10} {'Location':<12} {'Active'}")
            for t in tables:
                print(
                    f"  {t.get('tableID'):<8} {t.get('tableNumber'):<6} {t.get('capacity'):<10} "
                    f"{t.get('location'):<12} {t.get('isActive')}"
                )

    elif choice == "11":
        print("\n--- Update Configuration ---")
        print("Keys: maxPartySize, graceMinutes, minNoticeMinutes, timeSlotMinutes")
        key = input("Enter config key: ").strip()
        value = input("Enter new value: ").strip()
        controller.update_config(key, value)

    elif choice == "12":
        print("\n--- System Configuration ---")
        config = controller.get_config()
        if config:
            for k, v in config.items():
                print(f"  {k}: {v}")

    elif choice == "13":
        controller.logout()

    elif choice == "14":
        return True

    else:
        log_error("Invalid option selected.", CAT_ERROR)

    return False


def main():
    controller = ReservationController()

    while True:
        display_header()
        if not controller.current_user:
            print("\n[ PUBLIC MENU ]")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            choice = input("\nSelect an option: ")
            if choice == "1":
                print("\n--- User Registration ---")
                name = input("Enter Name: ")
                email = input("Enter Email: ")
                password = input("Enter Password: ")
                phone = input("Enter Phone: ")
                reg_data = UserRegistration(name, email, password, phone)
                controller.register_user(reg_data)
            elif choice == "2":
                print("\n--- Login ---")
                email = input("Email: ")
                password = input("Password: ")
                controller.login(email, password)
            elif choice == "3":
                print("\nThank you for using the system. Goodbye!")
                break
            else:
                log_error("Invalid option selected.", CAT_ERROR)
        else:
            user_name = controller.current_user.get(FLD_NAME, "User")
            user_role = controller.current_user.get("role")
            is_admin = user_role == ROLE_STAFF and controller.current_user.get("staffRole") == ROLE_ADMIN
            print(f"\n[ WELCOME, {user_name.upper()} ]")

            if is_admin:
                if _admin_menu(controller):
                    print("\nClosing System...")
                    break
            elif user_role == ROLE_STAFF:
                if _staff_menu(controller):
                    print("\nClosing System...")
                    break
            else:
                if _customer_menu(controller):
                    print("\nClosing System...")
                    break


if __name__ == "__main__":
    main()
