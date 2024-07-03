import json

from optimizers.base_optimizer import BaseOptimizer


class RandomOptimizer(BaseOptimizer):
    def __init__(self, iterations):
        super().__init__()
        self.iterations: int = iterations

    def run_iteration(self) -> bool:
        solution = self.generate_random_solution()
        fitness = self.course_manager.rate_solution(solution)
        if fitness > self.best_fitness:
            self.best_fitness = fitness
            self.best_solution = solution
            print("New best solution found", self.best_fitness, self.best_solution)
            return True
        else:
            return False

    def run(self) -> None:
        for i in range(self.iterations):
            self.run_iteration()
        final_timetable = self.get_timetable_from_best_solution()

        print(final_timetable.to_str_full())

        groups = self.course_manager.get_classes_group_dict_from_solution(self.best_solution)
        print(json.dumps(groups, indent=4, default=str, ensure_ascii=False))

        print("All time best", self.best_fitness, self.best_solution)
