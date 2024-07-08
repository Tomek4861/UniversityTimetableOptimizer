# UniversityTimetableOptimizer

UniversityTimetableOptimizer is a schedule optimization application using genetic algorithms and a graphical interface created with PyQt6.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Running](#running)
- [Project Structure](#project-structure)
- [Instructions](#instructions)
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

## Instructions

1. Run the application:
    ```sh
    python main.py
    ```

2. Select correct semester.
3. Click `Add Course` and fill the Course Id.
4. TUTUAJ SCREEN. In the Dialog window you can blacklist groups - script will ignore them when creating a timetable. Why to do that? Because sometimes some classes groups may be full, or you don't want lessons with certain lecturer. In such cases simply put those groups separated by comma in the blacklist field. See examples[LINK] for more details.
5. Repeat steps 3-4 for all courses you want to add.
6. Click `Edit Travel Times.
7. Fill travel times for all time ranges. For most cases you can set one for whole day.
8. Exit the travel times window.
9. Click `Create Plan`.
10. Wait for the timetable to be created - new window will pop up with the timetable.
11. On the timetable window you can see the generated timetable week by week.
12. You can click `Create Plan` button multiple times to make sure that the timetable is optimal (but in most cases it is).
### Saving Timetable
All files are being saved in project directory to `\Timetables\D_M_Y_H-M-S`. For example `\Timetables\08_07_2024_17-23-20`. 

You can find there:
- `timetable.json` - JSON file containing whole generated timetable day by day.
- `groups.csv` - CSV file containing selected groups for each course.
- Optionally you can save week schedule as an `.png` image by clicking `Save Screenhost` button.



## Usage Example
1. After selecting semester, I add all courses required in the semester, so I copy from USOS all ids.
2. Let's say that I'm lazy and I don't want to participate in any classed before 9:00. 
So, using data from USOS I blacklist all groups from all courses that have classes before 9:00.
3. Next I set travel times. Because I travel by car, I set higher times for peak hours.
4. I click `Create Plan` and wait for the timetable to be generated.

Using the blacklisting feature you can easily avoid classes with lecturers you don't like, or classes that are too early or too late for you.


## Contributions

Would you like to help improve this project? Great! Feel free to report issues and submit pull requests.

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
