import json
import os.path


class ConfigManager:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(ConfigManager, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        self.path: str = self.deduct_path()

        self.config: dict = self.read()

    def get_blacklisted_groups_for_course(self, course_name):
        for course in self.config['courses']:
            if course['id'] == course_name:
                return course['blacklistedGroups']
        return []

    @staticmethod
    def deduct_path() -> str:
        parent_directory = os.path.dirname(os.path.abspath(__file__))
        base_directory = os.path.dirname(parent_directory)

        new_path = os.path.join(base_directory, 'config.json')
        return new_path

    def read(self) -> dict:
        with open(self.path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def get_key(self, key) -> any:
        return self.config[key]

    def get_blacklisted_groups(self, course_name, course_type) -> list[int]:
        for course in self.config['courses']:
            if course['id'] == course_name:
                return course['blacklistedGroups'][course_type]
        return []

    def get_term(self) -> str:
        return self.config['term']

    def set_blacklisted_groups_for_course(self, course_type, blacklisted_groups) -> None:
        for course in self.config['courses']:
            if course['id'] == course_type:
                course['blacklistedGroups'] = blacklisted_groups
                self.save()
                return
        else:
            self.config['courses'].append(dict(id=course_type, blacklistedGroups=blacklisted_groups))
            self.save()

    def remove_course(self, course_id) -> None:
        self.config['courses'] = [course for course in self.config['courses'] if course['id'] != course_id]
        self.save()

    def get_all_courses(self) -> list[str]:
        return [course['id'] for course in self.config['courses']]

    def get_travel_times(self) -> list[dict[str, int]]:
        return self.config['travelTimes']

    def get_first_travel_time(self) -> int:
        if self.config['travelTimes']:
            return self.config['travelTimes'][0]['time']
        return 0

    def remove_travel_time(self, index) -> None:
        self.config['travelTimes'].pop(index)
        self.save()

    def add_travel_time(self, time, hour_start, hour_end) -> None:
        self.config['travelTimes'].append(dict(time=time, hourStart=hour_start, hourEnd=hour_end))
        self.config['travelTimes'].sort(key=lambda x: x['hourStart'])
        self.save()

    def save(self) -> None:
        with open(self.path, 'w', encoding='utf-8') as file:
            self.config['courses'] = sorted(self.config['courses'], key=lambda x: x['id'])
            json.dump(self.config, file, indent=4)

    def set_term(self, term) -> None:
        self.config['term'] = term
        self.save()
