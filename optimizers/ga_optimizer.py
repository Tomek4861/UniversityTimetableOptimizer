import json
import random

from optimizers.base_optimizer import BaseOptimizer


class Individual:
    def __init__(self, solution):
        self.solution: list[int] = solution
        self.fitness: int = 0

    def crossover(self, other) -> tuple['Individual', 'Individual']:
        solution1 = []
        solution2 = []
        for i in range(len(self.solution)):
            if random.random() < 0.5:
                solution1.append(self.solution[i])
                solution2.append(other.solution[i])
            else:
                solution1.append(other.solution[i])
                solution2.append(self.solution[i])

        return Individual(solution1), Individual(solution2)

    def mutate(self, mutation_probability: float, allowed_values: list[list[int]]) -> None:
        for i in range(len(self.solution)):
            if random.random() < mutation_probability:
                self.solution[i] = random.choice(allowed_values[i])

    def set_fitness(self, fitness) -> None:
        self.fitness = fitness

    def clone(self):
        return Individual(self.solution.copy())


class GAOptimizer(BaseOptimizer):

    def __init__(self, population_size, mutation_probability, crossover_probability, generations, elite_percentage):
        super().__init__()
        self.population_size: int = population_size
        self.mutation_probability: float = mutation_probability
        self.crossover_probability: float = crossover_probability
        self.generations: int = generations
        self.population: list[Individual] = []
        self.tournament_size: int = 4
        self.iterations_without_improvement_stop_threshold: int = 20
        self.elite_size: int = int(population_size * elite_percentage / 100)

    def calculate_fitness_all(self) -> None:
        for individual in self.population:
            individual.set_fitness(self.course_manager.rate_solution(individual.solution))

    def initialize_population(self) -> None:
        for i in range(self.population_size):
            solution = self.generate_random_solution()
            individual = Individual(solution)
            self.population.append(individual)

        self.calculate_fitness_all()

    def get_random_individuals(self, count=1) -> list[Individual]:
        return random.choices(self.population, k=count)

    def get_parent_pair_tournament(self) -> list[Individual]:
        participants = self.get_random_individuals(self.tournament_size)
        return sorted(participants, key=lambda x: x.fitness, reverse=True)[:2]

    def sort_population(self) -> None:
        self.population = sorted(self.population, key=lambda x: x.fitness, reverse=True)

    def run_iteration(self) -> bool:
        "Returns true if improvement was made, false otherwise"
        new_population = []
        self.keep_elite(new_population)
        while len(new_population) < self.population_size:
            parent1, parent2 = self.get_parent_pair_tournament()
            if random.random() < self.crossover_probability:
                child1, child2 = parent1.crossover(parent2)
                child1.mutate(self.mutation_probability, self.accepted_values)
                child2.mutate(self.mutation_probability, self.accepted_values)
                new_population.extend([child1, child2])
            else:
                new_population.extend([parent1.clone(), parent2.clone()])
        self.population = new_population
        for individual in self.population:
            individual.mutate(self.mutation_probability, self.accepted_values)

        self.calculate_fitness_all()
        self.sort_population()
        best_individual = self.population[0]
        if best_individual.fitness > self.best_fitness:
            self.best_fitness = best_individual.fitness
            self.best_solution = best_individual.solution
            print(f"New best solution found", self.best_fitness, self.best_solution)
            return True
        return False

    def keep_elite(self, new_population) -> None:
        # pop is already sorted
        for i in range(self.elite_size):
            individual = self.population[i].clone()
            # self.local_optimization(individual)
            new_population.append(individual)

    def run(self) -> None:
        self.initialize_population()
        iterations_without_improvement = 0
        for i in range(self.generations):
            print(f"Generation {i}")
            if was_improved := self.run_iteration():
                iterations_without_improvement = 0
            else:
                iterations_without_improvement += 1

            if iterations_without_improvement > self.iterations_without_improvement_stop_threshold:
                print("Stopping due to algorithm stagnation")
                break

        final_timetable = self.get_timetable_from_best_solution()

        print(final_timetable.to_str_full())

        groups = self.course_manager.get_classes_group_dict_from_solution(self.best_solution)
        print(json.dumps({str(k): v for k, v in groups.items()}, indent=4, default=str, ensure_ascii=False))

        print("All time best", self.best_fitness, self.best_solution)
        # print(json.dumps(final_timetable.to_ui_format(), indent=4, default=str, ensure_ascii=False))
        print(self.course_manager.cache_hits, "cache hits")
        print(self.course_manager.calculate_possible_solutions(), "possible solutions")
