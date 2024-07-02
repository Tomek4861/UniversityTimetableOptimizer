from abc import ABC, abstractmethod
from models.course_manager import CourseManager
import random


class BaseOptimizer(ABC):
    def __init__(self):
        self.course_manager: CourseManager = CourseManager()
        self.accepted_values = list(self.course_manager.get_group_ids_for_all_courses().values())
        self.best_solution = []
        self.best_fitness = 0


    def generate_random_solution(self):
        solution = []
        for course_name, course_group_ids in self.course_manager.get_group_ids_for_all_courses().items():
            solution.append(random.choice(course_group_ids))

        return solution

    @abstractmethod
    def run_iteration(self):
        pass

    @abstractmethod
    def run(self):
        pass

    def get_best_solution(self):
        return self.best_solution

    def get_best_fitness(self):
        return self.best_fitness

    def get_best_solution_as_dict(self):
        return self.course_manager.get_classes_group_dict_from_solution(self.best_solution)

    def get_timetable_from_best_solution(self):
        return self.course_manager.get_plan_from_solution(self.best_solution)
