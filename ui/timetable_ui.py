from PyQt6.QtCore import Qt, QTime, QDate, QDateTime
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QMessageBox, QPushButton, QLabel,
    QHBoxLayout
)
import qtawesome as qta

from models.timetable import TimeTable


class TimetableApp(QMainWindow):
    def __init__(self, timetable_object: TimeTable, final_fitness: float, window_id:int):
        super().__init__()
        self.timetable: QTableWidget = QTableWidget()
        self.current_week_start: QDateTime = QDateTime.currentDateTime()
        self.current_week_end: QDateTime = QDateTime.currentDateTime()
        self.timetable_manager: TimeTable = timetable_object
        self.setWindowTitle(f"Timetable {window_id} - Fitness: {final_fitness}")
        self.setWindowIcon(qta.icon('fa.calendar'))

        self.setGeometry(100, 100, 790, 770)
        self.setMaximumWidth(790)
        self.colors: list[QColor] = [
            QColor(200, 200, 255),
            QColor(255, 200, 200),
            QColor(200, 255, 200),
            QColor(255, 255, 200),
            QColor(255, 200, 255),
            QColor(200, 255, 255),
            QColor(255, 220, 180),
            QColor(220, 220, 255),
            QColor(180, 255, 220),
            QColor(220, 255, 180),
            QColor(255, 180, 220),
            QColor(240, 230, 140),
            QColor(255, 215, 180),
            QColor(200, 220, 255),
            QColor(220, 255, 200)
        ]
        self.course_colors: dict[str, QColor] = {}

        self.data_meetings_dict: list[dict[str,any]] = self.timetable_manager.to_ui_format()

        self.current_week_offset = 0
        self.initialize_timetable()

        self.layout: QVBoxLayout = QVBoxLayout()

        self.date_label: QLabel = QLabel()
        self.set_week_start_end()
        self.update_date_label()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_time = self.timetable_manager.get_total_university_time()
        self.fitness_label = QLabel(f"Total university time: {total_time}")
        self.fitness_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.fitness_label)

        self.layout.addWidget(self.date_label)
        self.layout.addWidget(self.timetable)

        self.prev_week_button: QPushButton = QPushButton("Week back")
        self.prev_week_button.setIcon(qta.icon('fa.arrow-left', color='white'))

        self.next_week_button: QPushButton = QPushButton("Week forward")
        self.next_week_button.setIcon(qta.icon('fa.arrow-right', color='white'))
        self.next_week_button.setLayoutDirection(Qt.LayoutDirection.RightToLeft) # icon on the right
        self.prev_week_button.setDisabled(True)

        self.prev_week_button.clicked.connect(self.previous_week)
        self.next_week_button.clicked.connect(self.next_week)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.prev_week_button)
        button_layout.addWidget(self.next_week_button)

        self.layout.addLayout(button_layout)

        self.save_screenshot_button: QPushButton = QPushButton("Save Screenshot")
        self.save_screenshot_button.setIcon(qta.icon('fa.save', color='white'))

        self.save_screenshot_button.clicked.connect(self.save_screenshot)
        self.layout.addWidget(self.save_screenshot_button, alignment=Qt.AlignmentFlag.AlignCenter)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.setStyleSheet(self.get_stylesheet())

        self.timetable.cellDoubleClicked.connect(self.show_details)

    def initialize_timetable(self) -> None:

        self.timetable.setColumnCount(7)
        self.timetable.setHorizontalHeaderLabels(
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

        self.timetable.setWordWrap(True)
        # self.timetable.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.timetable.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.update_timetable()

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
        }
        """

    def get_time_range(self) -> tuple[str, str]:
        min_time = QTime.fromString("23:59", "HH:mm")
        max_time = QTime.fromString("00:00", "HH:mm")
        for week_day, meeting_list in self.data_meetings_dict[self.current_week_offset]['week_meetings'].items():
            for meeting in meeting_list:
                start = QTime.fromString(meeting.get_start_time(), "HH:mm")
                end = QTime.fromString(meeting.get_end_time(), "HH:mm")
                if start < min_time:
                    min_time = start
                if end > max_time:
                    max_time = end

        # subtract 60 minutes from min_time and add 60 minutes to max_time
        min_time = min_time.addSecs(-60 * 60)
        max_time = max_time.addSecs(60 * 60)
        return min_time.toString("HH:mm"), max_time.toString("HH:mm")

    def generate_time_intervals(self, start_time, end_time, interval_minutes) -> list[str]:
        time_format = "HH:mm"
        start = QTime.fromString(start_time, time_format)
        end = QTime.fromString(end_time, time_format)
        times = []
        if not start.isValid() or not end.isValid():
            raise ValueError("Invalid time format")
        while start <= end:
            times.append(start.toString(time_format))
            start = start.addSecs(interval_minutes * 60)
        return times

    def set_custom_vertical_headers(self) -> None:
        headers = []
        for i, time in enumerate(self.time_intervals_30):
            if i % 2 == 0:
                headers.append(time)
            else:
                headers.append("")
        self.timetable.setVerticalHeaderLabels(headers)

    def time_to_row(self, time_str) -> int:

        # transforms time in HH:MM format to corresponding row index
        time_format = "HH:mm"
        time = QTime.fromString(time_str, time_format)
        for i, t in enumerate(self.time_intervals_30):
            interval_time = QTime.fromString(t, time_format)
            if time == interval_time:
                return i
            elif time < interval_time:
                return i if i == 0 else i - 1
        return len(self.time_intervals_30) - 1

    def clear_spans(self) -> None:
        for row in range(self.timetable.rowCount()):
            for column in range(self.timetable.columnCount()):
                if self.timetable.columnSpan(row, column) > 1 or self.timetable.rowSpan(row, column) > 1:
                    self.timetable.setSpan(row, column, 1, 1)

    def populate_timetable(self) -> None:
        # Clear existing items and spans
        self.timetable.clearContents()
        self.clear_spans()

        for week_day, meeting_list in self.data_meetings_dict[self.current_week_offset]['week_meetings'].items():
            for meeting in meeting_list:
                start_row = self.time_to_row(meeting.get_start_time())
                end_row = self.time_to_row(meeting.get_end_time())
                self.timetable.setSpan(start_row, week_day, end_row - start_row, 1)

                item = QTableWidgetItem(meeting.course_name)
                item.setToolTip("\n".join([meeting.lesson_type, f"{meeting.course_name}, gr. {meeting.group_id}", meeting.lecturer, f"{meeting.get_start_time()} — {meeting.get_end_time()}"]))
                item.setData(Qt.ItemDataRole.UserRole, meeting)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                # item.setFont(QFont('Verdana'))

                if meeting.course_name not in self.course_colors:
                    self.course_colors[meeting.course_name] = self.colors.pop(0)
                item.setBackground(self.course_colors[meeting.course_name])
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                self.timetable.setItem(start_row, week_day, item)

        # disable empty cells
        for row in range(self.timetable.rowCount()):
            for column in range(self.timetable.columnCount()):
                if not self.timetable.item(row, column):
                    item = QTableWidgetItem()
                    item.setFlags(Qt.ItemFlag.NoItemFlags)
                    self.timetable.setItem(row, column, item)

    def update_timetable(self) -> None:

        start_time, end_time = self.get_time_range()
        self.time_intervals_30 = self.generate_time_intervals(start_time, end_time, 30)

        self.timetable.setRowCount(len(self.time_intervals_30))
        self.set_custom_vertical_headers()

        self.populate_timetable()

    def show_details(self, row, column) -> None:
        item = self.timetable.item(row, column)
        if item:
            subject = item.text()

            details = item.data(Qt.ItemDataRole.UserRole)
            QMessageBox.information(self, subject, details.to_ui_string())

    def set_week_start_end(self) -> None:
        start_of_week = self.data_meetings_dict[self.current_week_offset]['week_start']
        end_of_week = self.data_meetings_dict[self.current_week_offset]['week_end']
        self.current_week_start = QDate(start_of_week)
        self.current_week_end = QDate(end_of_week)

    def update_date_label(self) -> None:
        self.date_label.setText(
            f"Timetable from {self.current_week_start.toString('dd MMM yyyy')} to {self.current_week_end.toString('dd MMM yyyy')}")

    def previous_week(self) -> None:
        self.current_week_offset -= 1
        self.set_week_start_end()

        self.update_date_label()
        self.update_timetable()
        if self.current_week_offset == 0:
            self.prev_week_button.setDisabled(True)

        self.next_week_button.setDisabled(False)

    def next_week(self) -> None:
        # print(self.current_week_offset, max(self.data_meetings_dict.keys()))
        self.current_week_offset += 1
        self.set_week_start_end()
        self.update_date_label()
        self.update_timetable()
        if self.current_week_offset == len(self.data_meetings_dict) - 1:
            self.next_week_button.setDisabled(True)

        self.prev_week_button.setDisabled(False)

    def activate_main_window(self) -> None:
        self.raise_()
        self.activateWindow()

    def save_screenshot(self) -> None:
        pixmap = self.timetable.grab()
        cat_name = self.timetable_manager.get_catalog_name()
        start_of_week_str = self.current_week_start.toString('dd_MM_yyyy')
        end_of_week_str = self.current_week_end.toString('dd_MM_yyyy')
        path = f'Timetables/{cat_name}/{start_of_week_str} - {end_of_week_str}.png'

        pixmap.save(path)
        print(f"Screenshot saved as {path}")
        # add dialog box with confirmation
        QMessageBox.information(self, "Screenshot saved", f"Screenshot successfully saved")
