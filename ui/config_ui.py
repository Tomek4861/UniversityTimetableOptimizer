from multiprocessing import Process
from PyQt6.QtWidgets import QApplication  # needed for qtawesome
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QLineEdit, QTableWidget,
    QTableWidgetItem, QMessageBox, QSpinBox, QDialog, QComboBox
)
import qtawesome as qta
from config.config_manager import ConfigManager
from utils.launcher import timetable_app_launcher
from utils.scraper import Scraper


class ConfigApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_manager: ConfigManager = ConfigManager()
        self.scraper: Scraper = Scraper()
        self.setWindowTitle("Timetable Optimizer")
        self.setWindowIcon(qta.icon('fa.cogs'))
        self.setGeometry(100, 100, 1150, 800)
        self.timetable_window_id = 1

        valid_semesters = self.scraper.get_valid_semesters()

        self.semester_combo_box: QComboBox = QComboBox()
        self.semester_combo_box.addItems(valid_semesters.keys())
        self.semester_combo_box.setCurrentText(self.config_manager.get_term())
        self.semester_combo_box.currentTextChanged.connect(self.set_new_semester_with_warning)
        self.semester_layout: QHBoxLayout = QHBoxLayout()
        self.semester_layout.addWidget(QLabel("Select Semester:"))
        self.semester_layout.addWidget(self.semester_combo_box)

        self.layout: QVBoxLayout = QVBoxLayout()
        self.layout.addLayout(self.semester_layout)

        self.course_table: QTableWidget = QTableWidget()
        self.course_table.setColumnCount(3)
        self.course_table.setHorizontalHeaderLabels(["Course ID", "Course Name", "Actions"])
        self.course_table.horizontalHeader().setStretchLastSection(True)
        self.course_table.horizontalHeader().setMinimumSectionSize(100)
        self.layout.addWidget(self.course_table)

        button_layout = QHBoxLayout()
        self.add_course_button: QPushButton = QPushButton("Add Course")
        self.add_course_button.setIcon(qta.icon('fa.plus', color='white'))

        self.add_course_button.clicked.connect(self.add_course_dialog)
        button_layout.addWidget(self.add_course_button)

        self.edit_travel_time_button: QPushButton = QPushButton("Edit Travel Time")
        self.edit_travel_time_button.setIcon(qta.icon('fa.clock-o', color='white'))
        self.edit_travel_time_button.clicked.connect(self.edit_travel_time_dialog)
        button_layout.addWidget(self.edit_travel_time_button)

        self.layout.addLayout(button_layout)

        self.create_plan_button: QPushButton = QPushButton("Create Plan")
        self.create_plan_button.setIcon(qta.icon('fa.calendar-check-o', color='white'))
        self.create_plan_button.clicked.connect(self.create_plan)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.create_plan_button)

        self.update_course_table()

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.setStyleSheet(self.get_stylesheet())

    def get_stylesheet(self) -> str:
        return """
        QMainWindow {
            background-color: #f0f0f0;
        }
        QLabel {
            font-size: 18px;
            font-weight: bold;
            color: #333333;
        }
        QPushButton {
            font-size: 16px;
            padding: 10px;
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
        }
        QPushButton:disabled {
            background-color: #CCCCCC;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QTableWidget {
            background-color: white;
            border: 1px solid #CCCCCC;
        }
        QHeaderView::section {
            background-color: #f2f2f2;
            padding: 4px;
            border: 1px solid #DDDDDD;
            font-size: 14px;
        }
        QTableWidget::item {
            padding: 5px;
            font-size: 16px;
        }
        QComboBox {
            font-size: 16px;
            padding: 5px;
            border: 1px solid #CCCCCC;
            border-radius: 5px;
            background-color: #ffffff;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: darkgray;
            border-left-style: solid; 
            border-top-right-radius: 3px; 
            border-bottom-right-radius: 3px;
        }
        QComboBox QAbstractItemView {
            border: 1px solid #CCCCCC;
            selection-background-color: #4CAF50;
            selection-color: white;
        }
        QScrollBar:vertical {
            background: #f0f0f0;
            width: 16px;
            margin: 16px 0 16px 0;
        }
        QScrollBar::handle:vertical {
            background: #CCCCCC;
            min-height: 20px;
            border-radius: 5px;
        }
        QScrollBar::add-line:vertical {
            background: #f0f0f0;
            height: 16px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }
        QScrollBar::sub-line:vertical {
            background: #f0f0f0;
            height: 16px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }
        """

    def update_course_table(self) -> None:
        self.course_table.setRowCount(0)
        courses_name_dict = {course_id: self.scraper.get_course_name_and_validate(course_id) for course_id in self.config_manager.get_all_courses()}
        courses_name_dict = dict(sorted(courses_name_dict.items(), key=lambda x: x[1]))


        for i, course_id in enumerate(courses_name_dict.keys()):
            self.course_table.insertRow(i)
            self.course_table.setRowHeight(i, 90)
            course_item = QTableWidgetItem(course_id)
            course_item.setFont(QFont('Arial', 16))
            course_item.setFlags(course_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.course_table.setItem(i, 0, course_item)
            # if not (course_name := self.scraper.get_course_name_and_validate(course_id)):
            #     course_name = "Invalid Course"
            course_name = courses_name_dict[course_id]

            name_item = QTableWidgetItem(course_name)
            name_item.setFont(QFont('Arial', 16))
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.course_table.setItem(i, 1, name_item)
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()

            actions_layout.setContentsMargins(0, 0, 0, 0)
            edit_button = QPushButton("Disable Class Groups")

            edit_button.setIcon(qta.icon('fa.ban', color='white'))
            edit_button.setObjectName("action_button")
            edit_button.setFixedSize(240, 30)
            edit_button.setStyleSheet(self.get_button_stylesheet())
            edit_button.clicked.connect(lambda _, cid=course_id: self.edit_course_dialog(cid))
            actions_layout.addWidget(edit_button)

            delete_button = QPushButton("Delete Course")
            delete_button.setIcon(qta.icon('fa.trash', color='white'))
            delete_button.setObjectName("action_button")
            delete_button.setFixedSize(160, 30)
            delete_button.setStyleSheet(self.get_button_stylesheet())
            delete_button.clicked.connect(lambda _, cid=course_id: self.delete_course(cid))
            actions_layout.addWidget(delete_button)

            actions_widget.setLayout(actions_layout)
            self.course_table.setCellWidget(i, 2, actions_widget)

        self.course_table.resizeColumnsToContents()
        self.course_table.setColumnWidth(2, 200)


    def get_button_stylesheet(self) -> str:
        return """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            min-height: 30px;
        }
        QPushButton:disabled {
            background-color: #CCCCCC;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        """

    def add_course_dialog(self) -> None:
        dialog = AddEditCourseDialog(self)
        dialog.exec()

    def edit_course_dialog(self, course_id) -> None:
        dialog = AddEditCourseDialog(self, course_id)
        dialog.exec()

    def delete_course(self, course_id) -> None:
        self.config_manager.remove_course(course_id)
        self.update_course_table()

    def edit_travel_time_dialog(self) -> None:
        dialog = TravelTimeManagerDialog(self)
        dialog.exec()

    def set_new_semester_with_warning(self, semester) -> None:
        if self.config_manager.get_term() != semester:
            self.config_manager.set_term(semester)
            QMessageBox.warning(self, "Warning", "Semester changed, make sure that all courses are still valid")
            self.update_course_table()

    def create_plan(self) -> None:

        if not self.config_manager.get_all_courses():
            QMessageBox.warning(self, "Error", "Add at least one course to create a plan")
            return

        p = Process(target=timetable_app_launcher, daemon=True, args=(self.timetable_window_id,))

        p.start()
        self.timetable_window_id += 1

        QMessageBox.information(self, "Create Plan", "New window with plan will come up in <30s!")


class AddEditCourseDialog(QDialog):
    def __init__(self, parent: ConfigApp, course_id=None):
        super().__init__(parent)
        self.parent: ConfigApp = parent
        self.course_id: Optional[str] = course_id
        self.setWindowTitle("Add/Edit Course")
        self.setWindowIcon(qta.icon('fa.edit'))
        self.setGeometry(150, 150, 400, 300)

        self.layout: QVBoxLayout = QVBoxLayout()

        self.course_id_label: QLabel = QLabel("Course ID:")
        self.course_id_input: QLineEdit = QLineEdit()
        self.course_id_input.setStyleSheet(self.get_lineedit_stylesheet())
        self.layout.addWidget(self.course_id_label)
        self.layout.addWidget(self.course_id_input)

        self.blacklisted_groups_layout: QVBoxLayout = QVBoxLayout()
        self.blacklisted_groups_label: QLabel = QLabel("Disabled Groups:")
        instructions_label = QLabel("Enter classes group numbers separated by commas")

        self.blacklisted_groups_layout.addWidget(self.blacklisted_groups_label)
        self.blacklisted_groups_layout.addWidget(instructions_label)
        self.blacklisted_groups: dict[str, QLineEdit] = {
            "Lecture": QLineEdit(),
            "Classes": QLineEdit(),
            "Laboratory": QLineEdit(),
            "Project": QLineEdit(),
            "Seminar": QLineEdit(),
        }
        for key, widget in self.blacklisted_groups.items():
            widget.setStyleSheet(self.get_lineedit_stylesheet())
            horizontal_layout = QHBoxLayout()
            horizontal_layout.addWidget(QLabel(f"{key : <15}\t"))
            horizontal_layout.addWidget(widget)
            self.blacklisted_groups_layout.addLayout(horizontal_layout)
        self.layout.addLayout(self.blacklisted_groups_layout)

        self.save_button: QPushButton = QPushButton("Save")
        self.save_button.setIcon(qta.icon('fa.save', color='white'))
        self.save_button.setStyleSheet(self.get_button_stylesheet())
        self.save_button.clicked.connect(self.save_course)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

        if self.course_id:
            self.load_course()

    def get_lineedit_stylesheet(self) -> str:
        return """
        QLineEdit {
            background-color: white; 
            border: 1px solid #CCCCCC;
            border-radius: 5px;
            padding: 5px;
            font-size: 14px;
        }
        """

    def get_button_stylesheet(self) -> str:
        return """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            padding: 10px;
            font-size: 16px;
        }
        QPushButton:disabled {
            background-color: #CCCCCC;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3e8e41;
        }
        """

    def load_course(self) -> None:
        self.course_id_input.setText(self.course_id)
        self.course_id_input.setDisabled(True)
        blacklisted_groups = self.parent.config_manager.get_blacklisted_groups_for_course(self.course_id)
        for key, widget in self.blacklisted_groups.items():
            widget.setText(','.join(map(str, blacklisted_groups[key])))

    def save_course(self) -> None:
        course_id = self.course_id_input.text().strip().upper()
        if not course_id:
            QMessageBox.warning(self, "Error", "Course ID cannot be empty")
            return

        if not (course_name := self.get_course_name_and_validate(course_id)):
            QMessageBox.warning(self, "Error", "Course ID is invalid")
            return

        try:
            blacklisted_groups = {class_type: list(map(int, bad_groups.text().split(','))) if bad_groups.text() else []
                                  for class_type, bad_groups in self.blacklisted_groups.items()}
        except ValueError:
            QMessageBox.warning(self, "Error", "Blacklisted groups must be a list of integers")
            return
        self.course_id = course_id
        self.parent.config_manager.set_blacklisted_groups_for_course(course_id, blacklisted_groups)
        self.parent.update_course_table()
        self.accept()

    def get_course_name_and_validate(self, course_id) -> str:
        course_id = course_id.upper()
        return self.parent.scraper.get_course_name_and_validate(course_id)


class TravelTimeManagerDialog(QDialog):
    def __init__(self, parent: ConfigApp):
        super().__init__(parent)
        self.parent: ConfigApp = parent
        self.setWindowTitle("Edit Travel Time")
        self.setWindowIcon(qta.icon('fa.clock-o'))
        self.setGeometry(200, 200, 800, 600)

        self.layout: QVBoxLayout = QVBoxLayout()
        self.times_table: QTableWidget = QTableWidget()
        self.times_table.setColumnCount(3)
        self.times_table.setHorizontalHeaderLabels(["Hours range", "Time (minutes)", "Actions"])
        self.times_table.horizontalHeader().setStretchLastSection(True)
        self.times_table.horizontalHeader().setMinimumSectionSize(100)
        self.layout.addWidget(self.times_table)

        button_layout = QHBoxLayout()
        self.add_interval_button: QPushButton = QPushButton("Add Time Interval")
        self.add_interval_button.setIcon(qta.icon('fa.plus', color='white'))
        self.add_interval_button.clicked.connect(self.add_time_interval)
        button_layout.addWidget(self.add_interval_button)

        self.save_times_button: QPushButton = QPushButton("Close and Save")
        self.save_times_button.setIcon(qta.icon('fa.save', color='white'))
        self.save_times_button.clicked.connect(self.save_times)
        button_layout.addWidget(self.save_times_button)
        self.update_times_table()

        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)

    def update_times_table(self) -> None:
        self.times_table.setRowCount(0)
        travel_times = self.parent.config_manager.get_travel_times()
        for i, travel_time_interval_dict in enumerate(travel_times):
            self.times_table.insertRow(i)
            self.times_table.setRowHeight(i, 90)
            start_hour = travel_time_interval_dict['hourStart']
            end_hour = travel_time_interval_dict['hourEnd']
            travel_time = travel_time_interval_dict['time']
            hours_item = QTableWidgetItem(f"{start_hour}:00 - {end_hour}:00")
            hours_item.setFont(QFont('Arial', 16))
            hours_item.setFlags(hours_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            hours_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.times_table.setItem(i, 0, hours_item)
            time_item = QTableWidgetItem(str(travel_time))
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            time_item.setFont(QFont('Arial', 16))
            time_item.setFlags(time_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.times_table.setItem(i, 1, time_item)
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            edit_button = QPushButton("Edit")
            edit_button.setIcon(qta.icon('fa.edit', color='white'))
            edit_button.setObjectName("action_button")
            edit_button.setFixedSize(160, 30)
            edit_button.setStyleSheet(self.get_button_stylesheet())
            edit_button.clicked.connect(lambda _, index=i: self.edit_time_interval_dialog(index))
            actions_layout.addWidget(edit_button)
            delete_button = QPushButton("Delete")
            delete_button.setIcon(qta.icon('fa.trash', color='white'))
            delete_button.setObjectName("action_button")
            delete_button.setFixedSize(160, 30)
            delete_button.setStyleSheet(self.get_button_stylesheet())
            delete_button.clicked.connect(lambda _, index=i: self.delete_time_interval(index))
            actions_layout.addWidget(delete_button)
            actions_widget.setLayout(actions_layout)
            self.times_table.setCellWidget(i, 2, actions_widget)
        self.times_table.resizeColumnsToContents()
        self.times_table.setColumnWidth(2, 200)
        self.times_table.setColumnWidth(1, 120)

    def get_button_stylesheet(self) -> str:
        return """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            min-height: 30px;
        }
        QPushButton:disabled {
            background-color: #CCCCCC;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        """

    def delete_time_interval(self, index) -> None:
        self.parent.config_manager.remove_travel_time(index)
        self.update_times_table()

    def edit_time_interval_dialog(self, index) -> None:
        dialog = AddEditTimeIntervalDialog(self, index)
        dialog.exec()

    def add_time_interval(self) -> None:
        dialog = AddEditTimeIntervalDialog(self)
        dialog.exec()

    def save_times(self) -> None:
        self.accept()


class AddEditTimeIntervalDialog(QDialog):
    def __init__(self, parent: TravelTimeManagerDialog, time_interval_index=None):
        self.parent: TravelTimeManagerDialog = parent
        super().__init__(parent)
        self.time_interval_index: Optional[int] = time_interval_index
        self.setWindowTitle("Add/Edit Time Interval")
        self.setWindowIcon(qta.icon('fa.plus-circle'))
        self.setGeometry(200, 200, 400, 300)
        self.layout: QVBoxLayout = QVBoxLayout()

        self.start_hour_spinbox: QSpinBox = QSpinBox()
        self.start_hour_spinbox.setRange(0, 24)
        self.start_hour_spinbox.setStyleSheet(self.get_spinbox_stylesheet())

        self.end_hour_spinbox: QSpinBox = QSpinBox()
        self.end_hour_spinbox.setRange(0, 24)
        self.end_hour_spinbox.setStyleSheet(self.get_spinbox_stylesheet())

        self.time_input: QSpinBox = QSpinBox()
        self.time_input.setRange(0, 1000)
        self.time_input.setStyleSheet(self.get_spinbox_stylesheet())

        self.layout.addWidget(QLabel("Start Hour"))
        self.layout.addWidget(self.start_hour_spinbox)
        self.layout.addWidget(QLabel("End Hour"))
        self.layout.addWidget(self.end_hour_spinbox)
        self.layout.addWidget(QLabel("Travel time (mins)"))
        self.layout.addWidget(self.time_input)

        self.save_button: QPushButton = QPushButton("Save")
        self.save_button.setIcon(qta.icon('fa.save', color='white'))
        self.save_button.setStyleSheet(self.get_button_stylesheet())
        self.save_button.clicked.connect(self.save_time_interval)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)
        if self.time_interval_index is not None:
            self.load_time_interval()

    def get_spinbox_stylesheet(self) -> str:
        return """
        QSpinBox {
            background-color: white; 
            border: 1px solid #CCCCCC;
            border-radius: 5px;
            padding: 5px;
            font-size: 14px;
        }
        QSpinBox::up-button {
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 16px;
            border: none;
        }
        QSpinBox::down-button {
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 16px;
            border: none;
        }
        """

    def get_button_stylesheet(self) -> str:
        return """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            padding: 10px;
            font-size: 16px;
        }
        QPushButton:disabled {
            background-color: #CCCCCC;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3e8e41;
        }
        """

    def are_overlaps(self, start_hour, end_hour) -> bool:
        travel_times = self.parent.parent.config_manager.get_travel_times()
        for i, time_interval in enumerate(travel_times):
            interval_start = time_interval['hourStart']
            interval_end = time_interval['hourEnd']

            if self.time_interval_index == i:
                continue

            if start_hour < interval_end and end_hour > interval_start:
                return True

        return False

    def load_time_interval(self) -> None:
        time_interval = self.parent.parent.config_manager.get_travel_times()[self.time_interval_index]
        self.start_hour_spinbox.setValue(time_interval['hourStart'])
        self.end_hour_spinbox.setValue(time_interval['hourEnd'])
        self.time_input.setValue(time_interval['time'])

    def save_time_interval(self) -> None:
        start_hour = self.start_hour_spinbox.value()
        end_hour = self.end_hour_spinbox.value()
        time = self.time_input.value()
        if not time:
            QMessageBox.warning(self, "Error", "Travel time cannot be empty")
            return
        if start_hour >= end_hour:
            QMessageBox.warning(self, "Error", "Start hour must be less than end hour")
            return

        if self.are_overlaps(start_hour, end_hour):
            QMessageBox.warning(self, "Error", "Overlapping time intervals are not allowed")
            return

        if self.time_interval_index is not None:
            self.parent.parent.config_manager.remove_travel_time(self.time_interval_index)
        self.parent.parent.config_manager.add_travel_time(time, start_hour, end_hour)
        self.parent.update_times_table()
        self.accept()
