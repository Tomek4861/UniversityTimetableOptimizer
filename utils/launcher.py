import sys

from PyQt6.QtWidgets import QApplication
from pytictoc import TicToc

from optimizers.ga_optimizer import GAOptimizer
from ui.timetable_ui import TimetableApp


def timetable_app_launcher(window_id: int):
    ptt = TicToc()
    ptt.tic()
    ga = GAOptimizer(population_size=2800, mutation_probability=0.015, crossover_probability=0.6, generations=90,
                     elite_percentage=5)
    ga.run()
    final_timetable = ga.get_timetable_from_best_solution()
    best_solution_dict = ga.get_best_solution_as_dict()

    ptt.toc("Time elapsed for algorithm")

    print(final_timetable.to_str_full())
    final_timetable.save_plan(best_solution_dict)


    app = QApplication(sys.argv + ['-platform', 'windows:darkmode=0'])
    window = TimetableApp(final_timetable, ga.best_fitness, window_id)
    window.show()
    window.activate_main_window()
    sys.exit(app.exec())
