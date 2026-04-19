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
)
from src.utils.error_handler import log_error


def display_header():
    print("\n" + "=" * 45)
    print("      RESTAURANT RESERVATION SYSTEM")
    print("=" * 45)


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
            print(f"\n[ WELCOME, {user_name.upper()} ]")

            if user_role == ROLE_STAFF:
                print("1. Create Walk-in Reservation")
                print("2. Cancel a Reservation")
                print("3. Logout")
                print("4. Exit Program")
                choice = input("\nSelect an option: ")
                if choice == "1":
                    print("\n--- Walk-in Reservation ---")
                    try:
                        party_input = input("Enter Party Size: ")
                        party_size = int(party_input)
                        controller.create_walkin_reservation([], party_size)
                    except ValueError:
                        log_error("Party size must be a number.", CAT_ERROR)
                elif choice == "2":
                    print("\n--- Cancel Reservation ---")
                    reservation_id = input("Enter Reservation ID: ")
                    controller.cancel_reservation(reservation_id.strip())
                elif choice == "3":
                    controller.logout()
                elif choice == "4":
                    print("\nClosing System...")
                    break
                else:
                    log_error("Invalid option selected.", CAT_ERROR)
            else:
                print("1. Make a Reservation")
                print("2. View My Reservations")
                print("3. Cancel a Reservation")
                print("4. Logout")
                print("5. Exit Program")
                choice = input("\nSelect an option: ")
                if choice == "1":
                    print("\n--- New Reservation ---")
                    reservation_date = input("Enter Date (YYYY-MM-DD): ")
                    start_time = input("Enter Start Time (HH:MM): ")
                    try:
                        party_input = input("Enter Party Size: ")
                        party_size = int(party_input)
                        request = BookingRequest(
                            customer_id=None,
                            table_ids=[],
                            date=reservation_date.strip(),
                            start_time=start_time.strip(),
                            party_size=party_size,
                            res_type=TYPE_ONLINE,
                        )
                        controller.make_reservation(request)
                    except ValueError:
                        log_error("Party size must be a number.", CAT_ERROR)
                elif choice == "2":
                    print("\n--- My Reservations ---")
                    history = controller.view_reservation_history()
                    if not history:
                        print("No reservations found.")
                    else:
                        for res in history:
                            print(
                                f"  {res.get('reservationID')} | {res.get('date')} {res.get('startTime')} | "
                                f"Party: {res.get('partySize')} | Status: {res.get('status')}"
                            )
                elif choice == "3":
                    print("\n--- Cancel Reservation ---")
                    reservation_id = input("Enter Reservation ID: ")
                    controller.cancel_reservation(reservation_id.strip())
                elif choice == "4":
                    controller.logout()
                elif choice == "5":
                    print("\nClosing System...")
                    break
                else:
                    log_error("Invalid option selected.", CAT_ERROR)


if __name__ == "__main__":
    main()
