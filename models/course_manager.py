import math

from config.config_manager import ConfigManager
from models.course import Course
from models.timetable import TimeTable
from utils.scraper import Scraper


class CourseManager:
    def __init__(self):
        self.scraper: Scraper = Scraper()
        self.config: ConfigManager = ConfigManager()
        self.courses: list[Course] = []
        self.course_groups_dict: dict[str, list[int]] = {}
        self.load_courses()
        self.fitness_cache: dict[tuple, float] = {}
        self.cache_hits: int = 0

    def load_courses(self) -> None:

        for course_id in self.config.get_all_courses():
            self.courses.extend(self.scraper.get_course_info(course_id))

        for course in self.courses:
            if not course.groups:
                print("Removing course", course.name, course.main_id, "because it has no groups")
                self.courses.remove(course)

        self.course_groups_dict = {course.main_id: course.get_group_ids() for course in self.courses}
        pass

    def get_group_ids_for_course(self, course_id: str) -> list[int]:
        return self.course_groups_dict[course_id]

    def get_group_ids_for_all_courses(self) -> dict[str, list[int]]:
        return self.course_groups_dict

    def validate_solution(self, solution: list[int]):
        if len(solution) != len(self.courses):
            raise ValueError("Invalid solution length")
        for course, group_id in zip(self.courses, solution):
            if group_id not in course.get_group_ids():
                raise ValueError(f"Invalid group id {group_id} for course {course.name} {course.main_id}")

    def rate_solution(self, solution: list[int]) -> float:
        solution_tuple = tuple(solution)
        if solution_tuple in self.fitness_cache:
            self.cache_hits += 1
            return self.fitness_cache[solution_tuple]
        self.validate_solution(solution)
        timetable = TimeTable()
        for course, group_id in zip(self.courses, solution):
            meets = course.get_all_meetings_for_group(group_id)
            timetable.add_meetings(meets)
        timetable.sort_meetings()
        if timetable.check_for_overlaps():
            # print("Bad solution - overlaps found")
            return 0
        total_time = timetable.get_total_university_time()
        # print(f"Total time for solution is {total_time}")
        # print(f"Total time for solution is {total_time.total_seconds() / 60}")
        fitness = 1 / (total_time.total_seconds() / 60)
        # print(f"Fitness for solution is {fitness}")
        self.fitness_cache[solution_tuple] = fitness
        return fitness

    def get_plan_from_solution(self, solution: list[int]) -> TimeTable:
        self.validate_solution(solution)
        timetable = TimeTable()
        for course, group_id in zip(self.courses, solution):
            meets = course.get_all_meetings_for_group(group_id)
            timetable.add_meetings(meets)
        timetable.sort_meetings()
        return timetable

    def get_classes_group_dict_from_solution(self, solution: list[int]) -> dict[tuple[str, str, str], int]:
        self.validate_solution(solution)
        classes_group_dict = {}
        for course, group_id in zip(self.courses, solution):
            classes_group_dict[(course.name, course.raw_id, course.type)] = group_id
        return classes_group_dict

    def calculate_possible_solutions(self) -> int:
        return math.prod([len(course.get_group_ids()) for course in self.courses])
