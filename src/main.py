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
            print(f"\n[ WELCOME, {user_name.upper()} ]")
            print("1. Make a Reservation")
            print("2. Logout")
            print("3. Exit Program")
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
                controller.logout()
            elif choice == "3":
                print("\nClosing System...")
                break
            else:
                log_error("Invalid option selected.", CAT_ERROR)


if __name__ == "__main__":
    main()
