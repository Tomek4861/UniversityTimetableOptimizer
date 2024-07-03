from datetime import datetime, timedelta
from typing import Any


class Meeting:
    def __init__(self, start_time: str, end_time: str, lecturer: str, group_id: int, parent):
        self.start_time: datetime = self.convert_to_datetime(start_time)
        self.end_time: datetime = self.convert_to_datetime(end_time)
        self.course_name: str = parent.name
        self.lecturer: str = lecturer
        self.group_id: int = group_id
        self.lesson_type: str = parent.type
        self.parent: object = parent

    def get_weekday(self) -> int:
        "Returns 0 for Monday, 1 for Tuesday, etc."
        return self.start_time.weekday()

    def get_start_time(self) -> str:
        return self.start_time.strftime("%H:%M")

    def get_end_time(self) -> str:
        return self.end_time.strftime("%H:%M")

    def get_date_without_time(self) -> datetime:
        return self.start_time.replace(hour=0, minute=0, second=0, microsecond=0)

    def get_first_day_of_week(self) -> datetime:
        return self.start_time - timedelta(days=self.get_weekday())

    def get_last_day_of_week(self) -> datetime:
        return self.get_first_day_of_week() + timedelta(days=6)

    @staticmethod
    def convert_to_datetime(date: str) -> datetime:
        return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    def __str__(self):
        return f"{self.start_time} - {self.end_time} | {self.course_name} | {self.group_id} | {self.lecturer} | {self.lesson_type}"

    def __repr__(self):
        return f"Meeting(start_time={self.start_time}, end_time={self.end_time}, course_name={self.course_name}, group_id={self.group_id}, lecturer={self.lecturer}, lesson_type={self.lesson_type})"

    def is_overlapping(self, other: Any) -> bool:
        return self.start_time <= other.end_time and other.start_time <= self.end_time

    def to_ui_string(self) -> str:
        return (f"Nazwa kursu:\t{self.course_name}\n"
                f"Typ zajęć:\t{self.lesson_type}\n"
                f"Numer Grupy:\t{self.group_id}\n"
                f"Godzina:\t\t{self.get_start_time().format('HH:mm')} — {self.get_end_time().format('HH:mm')}\n"
                f"Prowadzący:\t{self.lecturer}")
