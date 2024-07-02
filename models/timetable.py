import csv
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

from config.config_manager import ConfigManager
from utils.meeting import Meeting


class TimeTable:
    def __init__(self):
        self.schedule: dict[datetime, list[Meeting]] = {}
        self.config = ConfigManager()
        hours_in_day = 24
        self.travel_times = {x: timedelta(minutes=0) for x in range(hours_in_day)}
        self.load_travel_times()
        self.catalog_name = None

    def load_travel_times(self):
        travel_config = self.config.get_travel_times()
        travel_config.sort(key=lambda x: x['hourStart'])
        for time_info in travel_config:
            start = time_info['hourStart']
            end = time_info['hourEnd']
            time = time_info['time']
            for i in range(start, end):
                if self.travel_times[i] != timedelta(minutes=0):
                    raise ValueError(f"Travel time {i} already set - probably overlapping times in config.json file.")
                self.travel_times[i] = timedelta(minutes=time)

    def add_meetings(self, meetings: list[Meeting]):
        for meet in meetings:
            meet_date = meet.get_date_without_time()
            if meet_date not in self.schedule:
                self.schedule[meet_date] = [meet]
            else:
                self.schedule[meet_date].append(meet)

    def sort_meetings(self):
        for date in self.schedule:
            self.schedule[date].sort(key=lambda meet: meet.start_time)

        self.schedule = dict(sorted(self.schedule.items(), key=lambda item: item[0]))

    def check_for_overlaps(self) -> bool:
        """Check for overlaps in schedule, max 1 overlap is allowed"""
        overlaps_count = 0
        for date in self.schedule:
            meetings = self.schedule[date]
            for i in range(len(meetings) - 1):
                if meetings[i].is_overlapping(meetings[i + 1]):
                    # print(f"Overlap found between {meetings[i]} and {meetings[i + 1]}")
                    overlaps_count += 1
                if overlaps_count > 1:
                    return True
        return False

    def get_total_university_time(self) -> timedelta:
        # meetings need to be sorted
        total_time = timedelta()
        for date in self.schedule:
            # old_time = total_time
            first_meet = self.schedule[date][0]
            last_meet = self.schedule[date][-1]
            total_time += last_meet.end_time - first_meet.start_time
            # matching travel time
            total_time += self.travel_times[first_meet.start_time.hour]
            total_time += self.travel_times[last_meet.end_time.hour]
            # print(f"Estimated time for {date.strftime('%d.%m.%Y')} is {total_time - old_time}",
            #       f"from {first_meet.start_time} to {last_meet.end_time}", self.schedule[date])
        return total_time

    def to_dict(self):
        return {date.strftime('%d.%m.%Y'): [str(meet) for meet in meets] for date, meets in self.schedule.items()}

    def to_ui_format(self) -> List[Dict[str, Any]]:
        """
        Returns a list of dictionaries, where each dictionary represents a week
                 with days of the week and a list of meetings, as well as the start and end dates of the week.
        """
        weeks = {}
        for date_obj, meets in self.schedule.items():
            week = date_obj.isocalendar()[1]  # means week number in year
            if week not in weeks:
                weeks[week] = {}
            weeks[week][date_obj.weekday()] = meets

        weeks_but_as_list: List[Dict[str, Any]] = []
        for week_num, week_meetings in weeks.items():
            first_meeting = next(iter(week_meetings.values()))[0]

            week_start = first_meeting.get_first_day_of_week()
            week_end = first_meeting.get_last_day_of_week()
            weeks_but_as_list.append(dict(week_meetings=week_meetings, week_start=week_start, week_end=week_end))

        return weeks_but_as_list

    def to_str_full(self):
        return json.dumps(self.to_dict(), indent=4, default=str, ensure_ascii=False)

    def get_catalog_name(self):
        if not self.catalog_name:
            self.catalog_name = datetime.now().strftime("%d_%m_%Y_%H-%M-%S")
        return self.catalog_name

    def save_plan(self, course_solution_dict: dict[(str, str, str), int]):
        # create catalog if not exists
        if not os.path.exists(f"Timetables/{self.get_catalog_name()}"):
            os.makedirs(f"Timetables/{self.get_catalog_name()}")

        with open(f"Timetables/{self.get_catalog_name()}/timetable.json", 'w', encoding='utf-8') as file:
            json.dump(self.to_dict(), file, indent=4, default=str, ensure_ascii=False)

        with open(f"Timetables/{self.get_catalog_name()}/groups.csv", 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            headlines = ["Course Name", "Course ID", "Course Type", "Group ID"]
            writer.writerow(headlines)
            for (course_name, course_id, course_type), group_id in course_solution_dict.items():
                writer.writerow([course_name, course_id, course_type, group_id])
