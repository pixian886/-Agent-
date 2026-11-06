"""课程内容加载与校验。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import markdown

from app.config import CONTENT_DIR

EXERCISE_TYPES = {"single_choice", "fill_blank", "coding", "local_task", "trajectory_task"}
TYPE_LABELS = {
    "single_choice": "单选题",
    "fill_blank": "填空题",
    "coding": "编程题",
    "local_task": "本地作业",
    "trajectory_task": "轨迹题",
}
TRAJECTORY_RULE_LABELS = {
    "required_tool": "必需工具",
    "tool_order": "工具顺序",
    "max_steps": "最大步数",
    "min_steps": "最少步数",
    "max_tool_calls": "工具调用上限",
    "forbidden_tool": "禁止工具",
    "final_answer_contains": "最终答案关键词",
    "no_error_steps": "无错误步骤",
}


class ContentError(RuntimeError):
    """课程文件缺失或格式错误。"""


@dataclass(slots=True)
class TestCase:
    stdin: str
    expected_stdout: str


@dataclass(slots=True)
class Exercise:
    id: str
    lesson_id: str
    type: str
    title: str
    description: str = ""
    options: list[str] = field(default_factory=list)
    answer_index: int | None = None
    answers: list[str] = field(default_factory=list)
    case_sensitive: bool = False
    explanation: str = ""
    starter_code: str = ""
    timeout_seconds: int = 3
    test_cases: list[TestCase] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    answer: str = ""
    answer_code: str = ""
    common_errors: list[str] = field(default_factory=list)
    mock_http: dict | None = None
    task_id: str = ""
    rules: list[dict] = field(default_factory=list)
    starter_example: str = ""

    @property
    def type_label(self) -> str:
        """返回给模板使用的中文题型名称。"""
        return TYPE_LABELS.get(self.type, self.type)


@dataclass(slots=True)
class Lesson:
    id: str
    stage_id: str
    title: str
    content_html: str
    exercises: list[Exercise] = field(default_factory=list)
    exercise_ids: list[str] = field(default_factory=list)
    prev_lesson_id: str | None = None
    next_lesson_id: str | None = None
    course_id: str = "python"
    kind: str = "lesson"


@dataclass(slots=True)
class Stage:
    id: str
    title: str
    lessons: list[Lesson] = field(default_factory=list)


@dataclass(slots=True)
class Course:
    id: str
    title: str
    stages: list[Stage]
    lessons: list[Lesson]
    lesson_map: dict[str, Lesson]
    exercise_map: dict[str, Exercise]
    stage_map: dict[str, Stage]
    description: str = ""
    prerequisite: str | None = None

    @property
    def total_lessons(self) -> int:
        return len(self.lessons)

    def get_lesson(self, lesson_id: str) -> Lesson | None:
        return self.lesson_map.get(lesson_id)

    def get_exercise(self, exercise_id: str) -> Exercise | None:
        return self.exercise_map.get(exercise_id)

    def get_stage_for_lesson(self, lesson: Lesson) -> Stage:
        return self.stage_map[lesson.stage_id]

    def continue_lesson(self, completed_ids: set[str]) -> Lesson | None:
        """返回本课程第一门未完成课时；全部完成时返回 None。"""
        for lesson in self.lessons:
            if lesson.id not in completed_ids:
                return lesson
        return None


@dataclass(slots=True)
class CourseCatalog:
    courses: dict[str, Course]
    lesson_map: dict[str, Lesson]
    exercise_map: dict[str, Exercise]

    @property
    def ordered_courses(self) -> list[Course]:
        return list(self.courses.values())

    def get_course(self, course_id: str) -> Course | None:
        return self.courses.get(course_id)

    def get_lesson(self, lesson_id: str) -> Lesson | None:
        return self.lesson_map.get(lesson_id)

    def get_exercise(self, exercise_id: str) -> Exercise | None:
        return self.exercise_map.get(exercise_id)

    def get_course_for_lesson(self, lesson_id: str) -> Course | None:
        lesson = self.get_lesson(lesson_id)
        return self.courses.get(lesson.course_id) if lesson else None

    def get_course_for_exercise(self, exercise_id: str) -> Course | None:
        exercise = self.get_exercise(exercise_id)
        if exercise is None:
            return None
        lesson = self.get_lesson(exercise.lesson_id)
        return self.courses.get(lesson.course_id) if lesson else None


COURSE_SOURCES = [
    {
        "id": "python",
        "course_file": "course.json",
        "exercises_file": "exercises.json",
        "prerequisite": None,
    },
    {
        "id": "agent",
        "course_file": "agent_course.json",
        "exercises_file": "agent_exercises.json",
        "prerequisite": "python",
    },
]

_catalog: CourseCatalog | None = None


def init_course(content_dir: Path = CONTENT_DIR) -> CourseCatalog:
    """应用启动时加载课程目录，失败时阻止启动。"""
    global _catalog
    _catalog = load_catalog(content_dir)
    return _catalog


def get_catalog() -> CourseCatalog:
    """读取已加载的课程目录。"""
    if _catalog is None:
        raise RuntimeError("课程内容尚未加载，请先调用 init_course()")
    return _catalog


def get_course(course_id: str = "python") -> Course:
    """按课程 ID 读取课程；默认 Python，兼容旧调用。"""
    course = get_catalog().get_course(course_id)
    if course is None:
        raise RuntimeError(f"课程不存在：{course_id}")
    return course


def get_lesson(lesson_id: str) -> Lesson | None:
    """跨课程查找课时。"""
    return get_catalog().get_lesson(lesson_id)


def get_exercise(exercise_id: str) -> Exercise | None:
    """跨课程查找练习。"""
    return get_catalog().get_exercise(exercise_id)


def load_catalog(content_dir: Path = CONTENT_DIR) -> CourseCatalog:
    """加载所有课程并校验跨课程 ID 唯一性。"""
    content_dir = content_dir.resolve()
    courses: dict[str, Course] = {}
    lesson_map: dict[str, Lesson] = {}
    exercise_map: dict[str, Exercise] = {}

    for source in COURSE_SOURCES:
        course = _load_course(
            content_dir=content_dir,
            course_filename=source["course_file"],
            exercises_filename=source["exercises_file"],
            course_id=source["id"],
            prerequisite=source["prerequisite"],
        )
        if course.id in courses:
            raise ContentError(f"课程 ID 重复：{course.id}")
        courses[course.id] = course

        for lesson in course.lessons:
            if lesson.id in lesson_map:
                raise ContentError(f"课时 ID 跨课程重复：{lesson.id}")
            lesson_map[lesson.id] = lesson

        for exercise in course.exercise_map.values():
            if exercise.id in exercise_map:
                raise ContentError(f"练习 ID 跨课程重复：{exercise.id}")
            exercise_map[exercise.id] = exercise

    for course in courses.values():
        if course.prerequisite and course.prerequisite not in courses:
            raise ContentError(
                f"课程 {course.id} 的先修课程不存在：{course.prerequisite}"
            )
        if course.prerequisite == course.id:
            raise ContentError(f"课程 {course.id} 不能以自己为先修")

    return CourseCatalog(
        courses=courses,
        lesson_map=lesson_map,
        exercise_map=exercise_map,
    )


def load_course(content_dir: Path = CONTENT_DIR) -> Course:
    """兼容旧调用：只加载 Python 课程。"""
    return _load_course(
        content_dir=content_dir.resolve(),
        course_filename="course.json",
        exercises_filename="exercises.json",
        course_id="python",
        prerequisite=None,
    )


def _load_course(
    content_dir: Path,
    course_filename: str,
    exercises_filename: str,
    course_id: str,
    prerequisite: str | None,
) -> Course:
    """读取并校验单门课程的结构、练习与课时 Markdown。"""
    course_path = content_dir / course_filename
    exercises_path = content_dir / exercises_filename

    course_data = _load_json(course_path, "课程结构")
    exercises_data = _load_json(exercises_path, "练习配置")

    if not isinstance(course_data, dict):
        raise ContentError(f"{course_path}：顶层必须是对象")
    if not isinstance(exercises_data, list):
        raise ContentError(f"{exercises_path}：顶层必须是数组")

    course_title = _require_str(course_data, "course_title", course_path)
    description = str(course_data.get("course_description", "")).strip()
    stages_data = _require_list(course_data, "stages", course_path)
    lessons_data = _require_list(course_data, "lessons", course_path)

    exercises = _load_exercises(exercises_data, exercises_path)
    stage_map = _load_stages(stages_data, course_path)
    lesson_map = _load_lessons(
        lessons_data,
        content_dir,
        exercises,
        stage_map,
        course_path,
        course_id,
    )

    used_lesson_ids: set[str] = set()
    for stage in stage_map.values():
        stage_data = _find_by_id(stages_data, stage.id, course_path)
        lesson_ids = _require_list(stage_data, "lesson_ids", course_path)
        if not lesson_ids:
            raise ContentError(f"{course_path}：阶段 {stage.id} 的 lesson_ids 不能为空")

        resolved: list[Lesson] = []
        for lesson_id in lesson_ids:
            if not isinstance(lesson_id, str):
                raise ContentError(f"{course_path}：阶段 {stage.id} 的 lesson_ids 必须是字符串")
            lesson = lesson_map.get(lesson_id)
            if lesson is None:
                raise ContentError(f"{course_path}：阶段 {stage.id} 引用了不存在的课时 {lesson_id}")
            if lesson.stage_id != stage.id:
                raise ContentError(
                    f"{course_path}：课时 {lesson_id} 的 stage_id 与阶段 {stage.id} 不一致"
                )
            if lesson_id in used_lesson_ids:
                raise ContentError(f"{course_path}：课时 {lesson_id} 被多个阶段重复引用")
            used_lesson_ids.add(lesson_id)
            resolved.append(lesson)
        stage.lessons = resolved

    missing = set(lesson_map) - used_lesson_ids
    if missing:
        raise ContentError(
            f"{course_path}：以下课时没有被任何阶段引用：{', '.join(sorted(missing))}"
        )

    lessons = [lesson for stage in stage_map.values() for lesson in stage.lessons]
    for index, lesson in enumerate(lessons):
        lesson.prev_lesson_id = lessons[index - 1].id if index > 0 else None
        lesson.next_lesson_id = lessons[index + 1].id if index < len(lessons) - 1 else None

    return Course(
        id=course_id,
        title=course_title,
        description=description,
        prerequisite=prerequisite,
        stages=list(stage_map.values()),
        lessons=lessons,
        lesson_map=lesson_map,
        exercise_map=exercises,
        stage_map=stage_map,
    )


def _load_json(path: Path, label: str):
    if not path.exists():
        raise ContentError(f"缺少{label}文件：{path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContentError(f"{path} JSON 格式错误：{exc}") from exc


def _load_exercises(data: list, path: Path) -> dict[str, Exercise]:
    exercises: dict[str, Exercise] = {}
    for index, item in enumerate(data):
        where = f"{path} 第 {index + 1} 个练习"
        if not isinstance(item, dict):
            raise ContentError(f"{where}：必须是对象")

        exercise_id = _require_str(item, "id", path)
        lesson_id = _require_str(item, "lesson_id", path)
        exercise_type = _require_str(item, "type", path)
        title = _require_str(item, "title", path)
        if exercise_type not in EXERCISE_TYPES:
            raise ContentError(f"{where}：未知题型 {exercise_type}")
        if exercise_id in exercises:
            raise ContentError(f"{path}：练习 ID 重复：{exercise_id}")

        exercise = Exercise(
            id=exercise_id,
            lesson_id=lesson_id,
            type=exercise_type,
            title=title,
            description=str(item.get("description", "")),
            explanation=str(item.get("explanation", "")),
            starter_code=str(item.get("starter_code", "")),
        )

        if exercise_type == "single_choice":
            options = item.get("options")
            if not isinstance(options, list) or len(options) < 2:
                raise ContentError(f"{where}：options 至少需要两个选项")
            if not all(isinstance(option, str) for option in options):
                raise ContentError(f"{where}：options 必须是字符串数组")
            answer_index = item.get("answer_index")
            if not isinstance(answer_index, int) or not 0 <= answer_index < len(options):
                raise ContentError(f"{where}：answer_index 超出选项范围")
            exercise.options = options
            exercise.answer_index = answer_index
        elif exercise_type == "fill_blank":
            answers = item.get("answers")
            if not isinstance(answers, list) or not answers:
                raise ContentError(f"{where}：answers 不能为空")
            if not all(isinstance(answer, str) for answer in answers):
                raise ContentError(f"{where}：answers 必须是字符串数组")
            exercise.answers = answers
            exercise.case_sensitive = bool(item.get("case_sensitive", False))
        elif exercise_type == "coding":
            timeout = item.get("timeout_seconds", 3)
            if not isinstance(timeout, int) or not 1 <= timeout <= 10:
                raise ContentError(f"{where}：timeout_seconds 必须是 1~10 的整数")
            raw_cases = item.get("test_cases")
            if not isinstance(raw_cases, list) or not raw_cases:
                raise ContentError(f"{where}：编程题至少需要一个测试用例")
            cases: list[TestCase] = []
            for case_index, raw_case in enumerate(raw_cases):
                if not isinstance(raw_case, dict):
                    raise ContentError(f"{where} 第 {case_index + 1} 个测试用例：必须是对象")
                stdin = raw_case.get("stdin", "")
                expected = raw_case.get("expected_stdout", "")
                if not isinstance(stdin, str) or not isinstance(expected, str):
                    raise ContentError(
                        f"{where} 第 {case_index + 1} 个测试用例：stdin 与 expected_stdout 必须是字符串"
                    )
                cases.append(TestCase(stdin=stdin, expected_stdout=expected))
            exercise.timeout_seconds = timeout
            exercise.test_cases = cases
            exercise.mock_http = _load_mock_http(item, where)
            answer_code = item.get("answer_code", "")
            if not isinstance(answer_code, str):
                raise ContentError(f"{where}：answer_code 必须是字符串")
            exercise.answer_code = answer_code
        elif exercise_type == "local_task":
            description = item.get("description")
            if not isinstance(description, str) or not description.strip():
                raise ContentError(f"{where}：本地作业必须有非空的 description")
            raw_steps = item.get("steps")
            if (
                not isinstance(raw_steps, list)
                or not raw_steps
                or not all(
                    isinstance(step, str) and step.strip() for step in raw_steps
                )
            ):
                raise ContentError(f"{where}：本地作业必须有非空的 steps 字符串数组")
            answer = item.get("answer")
            if not isinstance(answer, str) or not answer.strip():
                raise ContentError(f"{where}：本地作业必须有非空的 answer")
            raw_errors = item.get("common_errors", [])
            if not isinstance(raw_errors, list) or not all(
                isinstance(error, str) for error in raw_errors
            ):
                raise ContentError(f"{where}：common_errors 必须是字符串数组")
            if "test_cases" in item:
                raise ContentError(f"{where}：本地作业不能配置 test_cases")

            exercise.description = description
            exercise.steps = [step.strip() for step in raw_steps]
            exercise.answer = answer
            exercise.answer_code = str(item.get("answer_code", ""))
            exercise.common_errors = raw_errors
        elif exercise_type == "trajectory_task":
            task_id = item.get("task_id")
            if not isinstance(task_id, str) or not task_id.strip():
                raise ContentError(f"{where}：轨迹题必须有非空的 task_id")
            raw_rules = item.get("rules")
            if not isinstance(raw_rules, list) or not raw_rules:
                raise ContentError(f"{where}：轨迹题至少需要一条规则")
            rules = [
                _load_trajectory_rule(
                    raw_rule,
                    f"{where} 第 {rule_index + 1} 条规则",
                )
                for rule_index, raw_rule in enumerate(raw_rules)
            ]
            if "test_cases" in item:
                raise ContentError(f"{where}：轨迹题不能配置 test_cases")
            exercise.task_id = task_id.strip()
            exercise.rules = rules
            exercise.starter_example = str(item.get("starter_example", ""))
            exercise.description = str(item.get("description", ""))

        exercises[exercise_id] = exercise
    return exercises


def _load_trajectory_rule(raw: object, where: str) -> dict:
    """校验轨迹规则字段，并附加中文标签。"""
    if not isinstance(raw, dict):
        raise ContentError(f"{where}：必须是对象")

    rule_type = raw.get("type")
    if not isinstance(rule_type, str) or rule_type not in TRAJECTORY_RULE_LABELS:
        raise ContentError(f"{where}：未知规则类型 {rule_type!r}")

    rule = dict(raw)
    rule["label"] = TRAJECTORY_RULE_LABELS[rule_type]
    if rule_type == "required_tool":
        tool = rule.get("tool")
        if not isinstance(tool, str) or not tool.strip():
            raise ContentError(f"{where}：required_tool 需要非空的 tool")
        args = rule.get("args")
        if args is not None and (
            not isinstance(args, list)
            or not all(isinstance(arg, str) and arg for arg in args)
        ):
            raise ContentError(f"{where}：required_tool.args 必须是字符串数组")
    elif rule_type == "tool_order":
        tools = rule.get("tools")
        if (
            not isinstance(tools, list)
            or not tools
            or not all(isinstance(tool, str) and tool for tool in tools)
        ):
            raise ContentError(f"{where}：tool_order.tools 必须是非空字符串数组")
    elif rule_type in {"max_steps", "min_steps", "max_tool_calls"}:
        value = rule.get("value")
        if not isinstance(value, int) or isinstance(value, bool):
            raise ContentError(f"{where}：{rule_type}.value 必须是整数")
        if rule_type == "max_tool_calls":
            if not 0 <= value <= 50:
                raise ContentError(f"{where}：max_tool_calls.value 必须是 0~50")
        elif not 1 <= value <= 50:
            raise ContentError(f"{where}：{rule_type}.value 必须是 1~50")
    elif rule_type == "forbidden_tool":
        tool = rule.get("tool")
        if not isinstance(tool, str) or not tool.strip():
            raise ContentError(f"{where}：forbidden_tool 需要非空的 tool")
    elif rule_type == "final_answer_contains":
        value = rule.get("value")
        if not isinstance(value, str) or not value.strip():
            raise ContentError(f"{where}：final_answer_contains 需要非空的 value")
    elif rule_type == "no_error_steps":
        pass

    rule["summary"] = _trajectory_rule_summary(rule)
    return rule


def _trajectory_rule_summary(rule: dict) -> str:
    """把规则转成给页面展示的一句中文说明。"""
    rule_type = rule["type"]
    if rule_type == "required_tool":
        args = rule.get("args") or []
        suffix = f"，参数 {', '.join(args)}" if args else ""
        return f"调用 {rule['tool']}{suffix}"
    if rule_type == "tool_order":
        return "顺序：" + " → ".join(rule["tools"])
    if rule_type == "max_steps":
        return f"最多 {rule['value']} 步"
    if rule_type == "min_steps":
        return f"至少 {rule['value']} 步"
    if rule_type == "max_tool_calls":
        return f"工具调用不超过 {rule['value']} 次"
    if rule_type == "forbidden_tool":
        return f"不得调用 {rule['tool']}"
    if rule_type == "final_answer_contains":
        return f"最终答案包含「{rule['value']}」"
    if rule_type == "no_error_steps":
        return "不得出现 error 步骤"
    return rule_type


def _load_mock_http(item: dict, where: str) -> dict | None:
    """读取编程题的 mock HTTP 配置；没有配置时返回 None。"""
    raw = item.get("mock_http")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ContentError(f"{where}：mock_http 必须是对象")

    port = raw.get("port")
    if (
        not isinstance(port, int)
        or isinstance(port, bool)
        or not 1024 <= port <= 65535
    ):
        raise ContentError(f"{where}：mock_http.port 必须是 1024~65535 的整数")

    path = raw.get("path")
    if not isinstance(path, str) or not path.startswith("/"):
        raise ContentError(f"{where}：mock_http.path 必须以 / 开头")

    query_key = raw.get("query_key")
    if not isinstance(query_key, str) or not query_key.strip():
        raise ContentError(f"{where}：mock_http.query_key 必须是非空字符串")

    responses = raw.get("responses")
    if not isinstance(responses, dict) or not responses:
        raise ContentError(f"{where}：mock_http.responses 不能为空")

    return {
        "port": port,
        "path": path,
        "query_key": query_key,
        "responses": {str(key): value for key, value in responses.items()},
        "default": raw.get("default"),
    }


def _load_stages(data: list, path: Path) -> dict[str, Stage]:
    stages: dict[str, Stage] = {}
    for index, item in enumerate(data):
        where = f"{path} 第 {index + 1} 个阶段"
        if not isinstance(item, dict):
            raise ContentError(f"{where}：必须是对象")
        stage_id = _require_str(item, "id", path)
        title = _require_str(item, "title", path)
        if stage_id in stages:
            raise ContentError(f"{path}：阶段 ID 重复：{stage_id}")
        stages[stage_id] = Stage(id=stage_id, title=title)
    return stages


def _load_lessons(
    data: list,
    content_dir: Path,
    exercises: dict[str, Exercise],
    stage_map: dict[str, Stage],
    path: Path,
    course_id: str,
) -> dict[str, Lesson]:
    lessons: dict[str, Lesson] = {}
    content_root = content_dir.resolve()

    for index, item in enumerate(data):
        where = f"{path} 第 {index + 1} 个课时"
        if not isinstance(item, dict):
            raise ContentError(f"{where}：必须是对象")

        lesson_id = _require_str(item, "id", path)
        stage_id = _require_str(item, "stage_id", path)
        title = _require_str(item, "title", path)
        content_file = _require_str(item, "content_file", path)
        kind = str(item.get("kind", "lesson")).strip() or "lesson"
        if kind not in {"lesson", "project", "placeholder"}:
            raise ContentError(f"{where}：kind 必须是 lesson / project / placeholder")
        if lesson_id in lessons:
            raise ContentError(f"{path}：课时 ID 重复：{lesson_id}")
        if stage_id not in stage_map:
            raise ContentError(f"{where}：stage_id {stage_id} 不存在")

        lesson_path = (content_dir / content_file).resolve()
        if not lesson_path.is_relative_to(content_root):
            raise ContentError(f"{where}：content_file 必须位于 content/ 目录内")
        if not lesson_path.exists():
            raise ContentError(f"{where}：课时文件不存在：{lesson_path}")
        if not lesson_path.is_file():
            raise ContentError(f"{where}：课时路径不是文件：{lesson_path}")

        raw_text = lesson_path.read_text(encoding="utf-8")
        content_html = markdown.markdown(
            raw_text,
            extensions=["extra", "sane_lists"],
        )

        exercise_ids = item.get("exercise_ids", [])
        if not isinstance(exercise_ids, list) or not all(
            isinstance(exercise_id, str) for exercise_id in exercise_ids
        ):
            raise ContentError(f"{where}：exercise_ids 必须是字符串数组")

        resolved_exercises: list[Exercise] = []
        for exercise_id in exercise_ids:
            exercise = exercises.get(exercise_id)
            if exercise is None:
                raise ContentError(f"{where}：引用了不存在的练习 {exercise_id}")
            if exercise.lesson_id != lesson_id:
                raise ContentError(
                    f"{where}：练习 {exercise_id} 的 lesson_id 与课时 {lesson_id} 不一致"
                )
            resolved_exercises.append(exercise)

        lessons[lesson_id] = Lesson(
            id=lesson_id,
            stage_id=stage_id,
            title=title,
            content_html=content_html,
            exercises=resolved_exercises,
            exercise_ids=exercise_ids,
            course_id=course_id,
            kind=kind,
        )
    return lessons


def _require_str(data: dict, key: str, path: Path) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ContentError(f"{path}：字段 {key} 必须是非空字符串")
    return value


def _require_list(data: dict, key: str, path: Path) -> list:
    value = data.get(key)
    if not isinstance(value, list):
        raise ContentError(f"{path}：字段 {key} 必须是数组")
    return value


def _find_by_id(data: list, target_id: str, path: Path) -> dict:
    for item in data:
        if isinstance(item, dict) and item.get("id") == target_id:
            return item
    raise ContentError(f"{path}：找不到阶段 {target_id}")
