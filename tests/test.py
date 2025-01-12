import unittest
from datetime import timedelta

from config.config_manager import ConfigManager
from optimizers.ga_optimizer import GAOptimizer

unittest.TestLoader.sortTestMethodsUsing = None


def run_optimizer_without_ui():
    ga = GAOptimizer(population_size=2800, mutation_probability=0.015, crossover_probability=0.6, generations=90,
                     elite_percentage=5)
    print(ga.course_manager.config)
    ga.run()
    return ga


class Tests(unittest.TestCase):
    def setUp(self):
        self.mockup_config = {
            "term": "2024/25-Z", "courses": [{
                "id": "W04IST-SI0827G", "blacklistedGroups": {
                    "Lecture": [], "Classes": [], "Laboratory": [], "Project": [], "Seminar": []
                }
            }], "travelTimes": [{
                "time": 60, "hourStart": 0, "hourEnd": 24
            }]
        }
        self.config_manager = ConfigManager(
            mock_up_config=self.mockup_config)

        self.optimization = None

    def test_a_total_uni_time(self):
        self.optimization = run_optimizer_without_ui()
        total_uni_time = self.optimization.get_timetable_from_best_solution().get_total_university_time()
        expected_total_time = timedelta(days=2, hours=23, minutes=15)
        self.assertEqual(total_uni_time, expected_total_time)

    def test_b_zero_overlaps(self):
        self.optimization = run_optimizer_without_ui()
        self.assertFalse(self.optimization.get_timetable_from_best_solution().check_for_overlaps())

    def test_c_config(self):
        self.assertEqual(self.config_manager.get_term(), "2024/25-Z")
        self.assertEqual(self.config_manager.get_all_courses(), ["W04IST-SI0827G"])
        self.assertEqual(self.config_manager.get_travel_times(), [{"time": 60, "hourStart": 0, "hourEnd": 24}])

    def test_d_remove_course(self):
        self.config_manager.remove_course("W04IST-SI0827G")
        self.assertEqual(self.config_manager.get_all_courses(), [])

    def test_e_timetable_no_courses(self):
        with self.assertRaises(ValueError):
            run_optimizer_without_ui()

    def test_f_invalid_travel_time(self):
        self.config_manager.config['courses'] = [{
            "id": "W04IST-SI0827G", "blacklistedGroups": {
                "Lecture": [], "Classes": [], "Laboratory": [], "Project": [], "Seminar": []
            }
        }]

        self.config_manager.config['travelTimes'] = [{"time": 30, "hourStart": 10, "hourEnd": 12},
                                                     {"time": 60, "hourStart": 0, "hourEnd": 24}]
        with self.assertRaises(ValueError):
            self.optimization = run_optimizer_without_ui()

    def test_g_no_travel_time(self):
        self.config_manager.config["travelTimes"] = []
        self.optimization = run_optimizer_without_ui()
        self.assertEqual(self.optimization.get_timetable_from_best_solution().travel_times,
                         {x: timedelta(minutes=0) for x in range(24)})


if __name__ == '__main__':
    unittest.main()
