# restaurant-reservation-system

A simple command-line interface restaurant reservation system.

### Description

A mini and fun project that incorporates the principles behind Object-Oriented Design and Analysis.

### Features

- User registration with input validation
- User login and logout
- Reservation creation from the CLI
- Automatic table selection based on party size
- Table capacity checks
- Reservation date and time validation
- Prevention of double-booking for the same table and time
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

- Singleton: A class only has one instance. The _Restaurant_ class only has one instance.
- Factory: The **src/logic/reservation_factory.py** creates tables or users without making a mess.
- Data Transfer Object (DTO): The BookingRequest class in **src/logic/reservation_controller.py** pass data to reduce _Parameter Bloat_

#### Traceability

The file names match the diagrams.
