import requests

from config.config_manager import ConfigManager
from models.course import Course


class Scraper:

    def __init__(self, ):
        self.base_url = 'https://apps.usos.pwr.edu.pl/services'
        self._session = requests.Session()
        self.config = ConfigManager()

    def get_valid_semesters(self) -> [dict[str, str]]:

        params = dict(term_type='semester', active_only='true')
        response = self._session.get(f'{self.base_url}/terms/terms_index', params=params, timeout=15)
        return {term['id']: term['name']['en'] for term in response.json()}

    @staticmethod
    def _get_lecturer_name(lecturer_id: int, lecturers_dict: dict) -> str:
        for lecturer_info in lecturers_dict:
            if lecturer_info['id'] == str(lecturer_id):
                return f"{lecturer_info['first_name']} {lecturer_info['last_name']}"
        else:
            return "Unknown"

    def get_course_name_and_validate(self, course_id: str) -> str:
        params = dict(course_id=course_id, term_id=self.config.get_term(),
                      fields='course_id|course_name')
        response = self._session.get(f'{self.base_url}/courses/course_edition', params=params, timeout=15)
        if response.json().get('course_id') == course_id.upper():
            return response.json()['course_name']['pl']
        else:
            return ''

    def get_course_info(self, course_id: str) -> list[Course]:
        course_list = []
        params = dict(course_id=course_id, term_id=self.config.get_term(),
                      fields='course_id|course_name|term_id|homepage_url|profile_url|coordinators|lecturers|course_units_ids')
        response = self._session.get(f'{self.base_url}/courses/course_edition', params=params, timeout=15)
        course_unit_ids = response.json()['course_units_ids']
        name = response.json()['course_name']['pl']
        lecturers = response.json()['lecturers']
        for unit_id in course_unit_ids:
            course = Course(course_id, name, course_unit_id=unit_id)
            groups = self.get_groups(unit_id)
            if not groups:
                raise ValueError(
                    f"Course {course_id} {course.name} has no groups - check if it takes place in selected term.")
            for group in groups:
                group = int(group)  # fix for usos api being retarded and returning group number as float
                meetings, class_type, lecturer_id = self.get_group_meetings_and_info(unit_id, group)
                if not meetings:
                    continue
                lecturer_name = self._get_lecturer_name(lecturer_id, lecturers)
                course.update_type(class_type)
                course.add_group(group, meetings, lecturer_name, class_type)
            course_list.append(course)
        self.blacklist_groups_from_config(course_list)
        return course_list

    def blacklist_groups_from_config(self, courses: list[Course]) -> None:
        for course in courses:
            blacklisted_groups = self.config.get_blacklisted_groups(course.raw_id, course.type)
            for group in blacklisted_groups:
                course.blacklist_group(group)
                # print("Blacklisted group", group, "for", course.name)
            # print(course)

    def get_groups(self, course_unit_id: int) -> list[int]:
        #  https://apps.usos.pwr.edu.pl/services/courses/course_unit?course_unit_id=62142&fields=id|homepage_url|profile_url|class_groups"
        params = dict(course_unit_id=course_unit_id, fields='id|homepage_url|profile_url|class_groups')
        response = self._session.get(f'{self.base_url}/courses/course_unit', params=params, timeout=15)
        return [group['number'] for group in response.json()['class_groups']]

    def get_group_meetings_and_info(self, unit_id: int, group_id: int) -> tuple[list[dict[str, str]], str, int]:
        params = dict(unit_id=unit_id, group_number=group_id,
                      fields='type|start_time|end_time|name|url|course_id|course_name|classtype_name|lecturer_ids|group_number|classgroup_profile_url|building_name|building_id|room_number|room_id|unit_id|classtype_id|cgwm_id|frequency|sm_id')
        response = self._session.get(f'{self.base_url}/tt/classgroup_dates2', params=params, timeout=15)
        if not response.json():  # group has no meetings
            return [], "", 0
        class_type = response.json()[0]['classtype_name']['en']
        if lecturers_ids := response.json()[0]['lecturer_ids']:
            lecturer_id = lecturers_ids[0]
        else:
            lecturer_id = -1
        return [{"start_time": meeting['start_time'], 'end_time': meeting['end_time']} for meeting in
                response.json()], class_type, lecturer_id
