from models.meeting import Meeting


class Course:

    def __init__(self, course_id: str, course_name: str, course_unit_id: int):
        self.raw_id: str = course_id
        self.main_id: str = course_id  # main_id is course_id + type
        self.name: str = course_name
        self.unit_id: int = course_unit_id
        self.groups: list[dict[str, any]] = []
        self.type: str = ""

    def update_type(self, new_type: str) -> None:
        if not self.type:
            self.type = new_type
            self.main_id = f"{self.main_id}_{self.type.replace(' ', '_')}"

    def blacklist_group(self, group_id: int) -> None:
        for group in self.groups:
            if group['group_id'] == group_id:
                self.groups.remove(group)
                return
        else:
            print(f"Group {group_id} not found in {self.name}")

    def __str__(self) -> str:
        return f"{self.name} {self.main_id} {self.unit_id} {self.type} {self.groups}"

    def __repr__(self) -> str:
        return f"Course(course_id={self.main_id}, course_name={self.name}, course_unit_id={self.unit_id}, groups={self.groups})"

    def add_group(self, group_id: int, meetings: list[dict[str, str]], lecturer: str, lesson_type: str) -> None:
        self.groups.append(dict(group_id=group_id, lecturer=lecturer, meetings=
        [Meeting(start_time=meet["start_time"], end_time=meet["end_time"], lecturer=lecturer,
                 group_id=group_id, parent=self) for meet in meetings]))

    def get_group_ids(self) -> list[int]:
        return [group['group_id'] for group in self.groups]

    def get_all_meetings_for_group(self, group_id: int) -> list[Meeting]:
        for group in self.groups:
            if group['group_id'] == group_id:
                return group['meetings']
        return []
