from optimizers.ga_optimizer import GAOptimizer
from concurrent.futures import ThreadPoolExecutor, as_completed


class GATester:
    def __init__(self, ):
        self.testes_data_range = {
            "population_size": [1400, 3000],
            "mutation_probability": [0.01, 0.02],
            "crossover_probability": [0.6, 0.7],
            "generations": [80],
            "elite_percentage": list(range(0, 30, 2))
        }

        self.results = []

    def run_one_test(self, population_size, mutation_probability, crossover_probability, generations, elite_percentage):
        ga = GAOptimizer(population_size, mutation_probability, crossover_probability, generations, elite_percentage)
        ga.run()
        return ga.get_best_fitness()

    def run_tests(self):
        with ThreadPoolExecutor() as executor:
            future_to_params = {}
            for population_size in self.testes_data_range["population_size"]:
                for mutation_probability in self.testes_data_range["mutation_probability"]:
                    for crossover_probability in self.testes_data_range["crossover_probability"]:
                        for generations in self.testes_data_range["generations"]:
                            for elite_percentage in self.testes_data_range["elite_percentage"]:
                                for i in range(10):
                                    future = executor.submit(self.run_one_test, population_size, mutation_probability, crossover_probability, generations, elite_percentage)
                                    future_to_params[future] = (population_size, mutation_probability, crossover_probability, generations, elite_percentage)

            for future in as_completed(future_to_params):
                population_size, mutation_probability, crossover_probability, generations, elite_percentage = future_to_params[future]
                try:
                    best_fitness = future.result()
                    print("Best fitness:", best_fitness)
                    self.results.append((population_size, mutation_probability, crossover_probability, generations, elite_percentage, best_fitness))
                except Exception as exc:
                    print(f"Test generated an exception: {exc}")

        self.save_results()

    def save_results(self):
        # save as csv
        with open("results.csv", "w") as f:
            f.write("population_size,mutation_probability,crossover_probability,generations,elite_percentage,best_fitness\n")
            for result in self.results:
                f.write(f"{result[0]},{result[1]},{result[2]},{result[3]},{result[4]},{result[5]}\n")


if __name__ == "__main__":
    tester = GATester()
    tester.run_tests()