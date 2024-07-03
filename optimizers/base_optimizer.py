from abc import ABC, abstractmethod
from models.course_manager import CourseManager
import random
from models.timetable import TimeTable


class BaseOptimizer(ABC):
    def __init__(self):
        self.course_manager: CourseManager = CourseManager()
        self.accepted_values: list[list[int]] = list(self.course_manager.get_group_ids_for_all_courses().values())
        self.best_solution: list[int] = []
        self.best_fitness: int = 0


    def generate_random_solution(self) -> list[int]:
        solution = []
        for course_name, course_group_ids in self.course_manager.get_group_ids_for_all_courses().items():
            solution.append(random.choice(course_group_ids))

        return solution

    @abstractmethod
    def run_iteration(self) -> bool:
        pass

    @abstractmethod
    def run(self) -> None:
        pass

    def get_best_solution(self) -> list[int]:
        return self.best_solution

    def get_best_fitness(self) -> int:
        return self.best_fitness

    def get_best_solution_as_dict(self) -> dict[tuple[str, str, str], int]:
        return self.course_manager.get_classes_group_dict_from_solution(self.best_solution)

    def get_timetable_from_best_solution(self) -> TimeTable:
        return self.course_manager.get_plan_from_solution(self.best_solution)
