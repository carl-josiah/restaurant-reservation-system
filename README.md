# restaurant-reservation-system

A simple command-line interface restaurant reservation system.

### Description

A mini and fun project that incorporates the principles behind Object-Oriented Design and Analysis.

### Features

- User registration with input validation and bcrypt password hashing
- User login and logout
- Online reservation creation from the CLI
- Walk-in reservation creation (Staff only)
- Reservation cancellation
- View personal reservation history
- Automatic table selection based on party size
- Table capacity checks
- Reservation date and time validation
- Prevention of double-booking for the same table and time
- Role-based menus for Customers and Staff
- Clear error messages for invalid input
- Success messages for registration and reservations
- JSON-based data storage for users, tables, reservations, and config data
- Simple command-line interface for easy use

### Object-Oriented Design and Analysis Principles

#### Core Object-Oriented Principles

- Abstraction: The _User_ class is an abstraction. It hides the complexity.
- Inheritance: The **src/models/user.py** includes inheritance to support different types of people (customer and staff).
- Encapsulation: Keeps the attributes _safe_ by only allowing the methods to access them.

#### General Responsibility Assignment Principles (GRASP)

- Controller: The **src/logic/reservation_controller.py** file will receive the command instead of the UI **(main.py)** to coordinate the models.
- Information Expert: Every data in a class belongs where it should belong.
- Creator: The **src/logic/reservation_factory.py** file is responsible for "creating" objects, it won't have to worry about how a _Reservation_ is born.
- Low Coupling: The evidence is by the amount of folders and files, each has its own responsibility and does not rely on other files to operate properly.
- High Cohesion: Every file has one job.
- Protected Variations: The **src/utils/error_handler.py** file has a function that has the core logic for handling errors

#### SOLID Principles

- Single Responsibility Principle (SRP): The **src/utils/README.md** explains how the project supports SRP.
- Open/Closed Principle: The _User_ hierarchy allows for extension, adding a class does not need to change old ones.
- Liskov Substitution Principle: This is the reason for using inheritance. The system expects a _User_, and giving it _Customer_ or _Staff_ would not break the system.

#### Supported Design Patterns

"Proven" solutions to common problems.

- Singleton: ReservationController is implemented as a single coordinating instance per session.
- Factory: The **src/logic/reservation_factory.py** creates tables or users without making a mess.
- Data Transfer Object (DTO): The BookingRequest and UserRegistration classes in **src/logic/reservation_controller.py** reduce parameter bloat.

#### Traceability

| Design Class | Implementation File | Responsibility and Mapping Description |
| :--- | :--- | :--- |
| **ReservationController** | `src/logic/reservation_controller.py` | The primary control class. It coordinates the whole system logic such as make_reservation and register_user and also manages the session state while doing it. |
| **ReservationFactory** | `src/logic/reservation_factory.py` | The service class that encapsulates the creation logic for Reservation objects. |
| **StorageManager** | `src/persistence/storage_manager.py` | The persistence class that identifies as the repository facade. It protects the business logic from storage changes and abstracts the json file input and output. |
| **User, Customer, Staff** | `src/models/user.py` | Implements the actor-oriented classes using inheritance. The Customer and Staff inherited from the User class to handle specific parameters or data. |
| **Reservation** | `src/models/reservation.py` | An entity class that represents the core business information. It is the information expert. |
| **Table** | `src/models/table.py` | An entity class that holds the capacity and location of the tables. It is a real-world constraint. |
| **TimeSlot** | `src/models/time_slot.py` | An entity class that defines the recurring time windows for bookings. |
| **NotificationService** | `src/logic/notification_service.py` | A service class that supports low coupling since it decouples the notification logic from the reservation state management. |
| **Constants** | `src/utils/constants.py` | To make it easier to edit terms and keys, to make sure that it is consistent throughout all the files. |
