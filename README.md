# UniversityTimetableOptimizer

UniversityTimetableOptimizer is a schedule optimization application using genetic algorithms and a graphical interface created with PyQt6.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Running](#running)
- [Project Structure](#project-structure)
- [Usage Example](#usage-example)
- [Contributions](#contributions)
- [License](#license)

## Requirements

- Python 3.9 or later
- `PyQt6`
- `requests`
- `qtawesome`
- `pytictoc`

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Tomek4861/UniversityTimetableOptimizer
    ```


2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Running

To run the application, follow these steps:

1. Ensure all required packages are installed.
2. Run the main program file:
    ```sh
    python main.py
    ```

## Project Structure

```plaintext
UniversityTimetableOptimizer/
├── config/
│   ├── __init__.py
│   └── config_manager.py
├── models/
│   ├── __init__.py
│   ├── course.py
│   ├── course_manager.py
│   ├── meeting.py
│   └── timetable.py
├── optimizers/
│   ├── __init__.py
│   ├── base_optimizer.py
│   ├── ga_optimizer.py
│   └── random_optimizer.py
├── ui/
│   ├── __init__.py
│   ├── config_ui.py
│   └── timetable_ui.py
├── utils/
│   ├── __init__.py
│   ├── launcher.py
│   └── scraper.py
├── main.py
└── requirements.txt

```

## Usage Example

1. Run the application:
    ```sh
    python main.py
    ```

2. In the graphical interface, add courses, set travel time between classes, and generate an optimal schedule.