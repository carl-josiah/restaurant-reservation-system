# restaurant-reservation-system

A simple command-line interface restaurant reservation system.

### Description

A mini and fun project that incorporates the principles behind Object-Oriented Design and Analysis.

### Features

### Object-Oriented Design and Analysis Principles

#### Core Object-Oriented Principles

- Abstraction: The _User_ class is an abstraction. It hides the complexity.
- Inheritance: The **src/models/user.py** supports inheritance to support different types of people.
- Encapsulation: Keeps the attributes _safe_ by only allowing the methods to access them.

#### General Responsibility Assignment Principles (GRASP)

- Controller: The **src/logic/controller.py** file will receive the command instead of the UI **(main.py)** to coordinate the models.
- Information Expert: Every data in a class belongs where it should belong.
- Creator: The **src/logic/factory.py** file is responsible for "creating" objects, it won't have to worry about how a _Reservation_ is born.
- Low Coupling: The evidence is by the amount of folders and files, each has its own responsibility and does not rely on other files to operate properly.
- High Cohesion: Every file has one job.

#### SOLID Principles

- Single Responsibility Principle (SRS): The **src/utils/README.md** explains how the project supports SRS.
- Open/Closed Principle: The _User_ hierarchy allows for extension, adding a class does not need to change old ones.
- Liskov Substitution Principle: This is the reason for using inheritance. The system expects a _User_, and giving it _Customer_ or _Staff_ would not break the system.

#### Supported Design Patterns

"Proven" solutions to common problems.

- Singleton: A class only has one instance. The _Restaurant_ class only has one instance.
- Factory: The **src/logic/factory.py** To generate tables or users without making a mess.

#### Traceability

The file names match the diagrams.
