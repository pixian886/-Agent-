"""轨迹题：只解析 JSON 并按规则判定，不执行代码、不访问网络。"""

from __future__ import annotations

import json

from app.content import Exercise

MAX_JSON_BYTES = 100_000
MAX_STEPS = 50
MAX_STRING_LENGTH = 2000
ALLOWED_STEP_TYPES = {"thought", "action", "observation", "finish", "error"}


class TrajectoryError(ValueError):
    """轨迹 JSON 结构不合法。"""


def trajectory_size(data: object) -> int:
    """返回轨迹序列化后的字节数，用于接口限流。"""
    try:
        return len(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    except (TypeError, ValueError):
        return MAX_JSON_BYTES + 1


def evaluate_trajectory(exercise: Exercise, data: object) -> dict:
    """校验轨迹并逐条执行规则，返回可直接作为 API 响应的结果。"""
    try:
        steps = _validate(data, exercise)
    except TrajectoryError as exc:
        return {
            "status": "wrong_answer",
            "message": str(exc),
            "rule_results": [],
            "step_count": _step_count(data),
        }

    rule_results = []
    for rule in exercise.rules:
        passed, detail = _run_rule(rule, data)
        rule_results.append(
            {
                "rule": rule.get("type", ""),
                "label": rule.get("label", rule.get("type", "")),
                "passed": passed,
                "detail": detail,
            }
        )

    accepted = all(item["passed"] for item in rule_results)
    return {
        "status": "accepted" if accepted else "wrong_answer",
        "message": (
            "轨迹通过全部规则"
            if accepted
            else "轨迹有规则未通过，请查看下面的逐条结果"
        ),
        "rule_results": rule_results,
        "step_count": len(steps),
    }


def _validate(data: object, exercise: Exercise) -> list[dict]:
    if not isinstance(data, dict):
        raise TrajectoryError("轨迹必须是 JSON 对象")

    version = data.get("version")
    if version != 1:
        raise TrajectoryError("version 必须为 1")

    task_id = data.get("task_id")
    if not isinstance(task_id, str) or not task_id.strip():
        raise TrajectoryError("task_id 不能为空")
    if task_id != exercise.task_id:
        raise TrajectoryError(
            f"task_id 不匹配：应为 {exercise.task_id}，实际为 {task_id}"
        )

    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        raise TrajectoryError("steps 必须是非空数组")
    if len(steps) > MAX_STEPS:
        raise TrajectoryError(f"steps 最多 {MAX_STEPS} 步，当前 {len(steps)} 步")

    for index, step in enumerate(steps):
        where = f"第 {index + 1} 步"
        if not isinstance(step, dict):
            raise TrajectoryError(f"{where}必须是对象")
        step_type = step.get("type")
        if step_type not in ALLOWED_STEP_TYPES:
            raise TrajectoryError(
                f"{where}的 type 必须是 thought / action / observation / finish / error"
            )

        content = step.get("content")
        if content is not None:
            if not isinstance(content, str):
                raise TrajectoryError(f"{where}的 content 必须是字符串")
            _check_string(content, f"{where}的 content")

        if step_type == "action":
            tool = step.get("tool")
            if not isinstance(tool, str) or not tool.strip():
                raise TrajectoryError(f"{where}的 tool 不能为空")
            arguments = step.get("arguments")
            if not isinstance(arguments, dict):
                raise TrajectoryError(f"{where}的 arguments 必须是对象")
            for key in arguments:
                if not isinstance(key, str):
                    raise TrajectoryError(f"{where}的 arguments 键必须是字符串")

    final_answer = data.get("final_answer")
    if not isinstance(final_answer, str):
        raise TrajectoryError("final_answer 必须是字符串")
    _check_string(final_answer, "final_answer")

    model = data.get("model")
    if model is not None:
        if not isinstance(model, str):
            raise TrajectoryError("model 必须是字符串")
        _check_string(model, "model")

    return steps


def _check_string(value: str, where: str) -> None:
    if len(value) > MAX_STRING_LENGTH:
        raise TrajectoryError(f"{where}超过 {MAX_STRING_LENGTH} 字符")


def _step_count(data: object) -> int:
    if isinstance(data, dict) and isinstance(data.get("steps"), list):
        return len(data["steps"])
    return 0


def _run_rule(rule: dict, data: dict) -> tuple[bool, str]:
    rule_type = rule.get("type")
    steps = data.get("steps") or []
    actions = [step for step in steps if step.get("type") == "action"]

    if rule_type == "required_tool":
        tool = rule.get("tool")
        required_args = rule.get("args") or []
        matched = [step for step in actions if step.get("tool") == tool]
        if not matched:
            return False, f"未调用必需工具 {tool}"
        if required_args:
            for step in matched:
                arguments = step.get("arguments") or {}
                missing = [name for name in required_args if name not in arguments]
                if not missing:
                    return True, f"已调用 {tool}，参数包含 {', '.join(required_args)}"
            return False, f"调用了 {tool}，但缺少参数 {', '.join(required_args)}"
        return True, f"已调用 {tool}"

    if rule_type == "tool_order":
        expected = rule.get("tools") or []
        actual = [step.get("tool") for step in actions]
        cursor = 0
        for name in actual:
            if cursor < len(expected) and name == expected[cursor]:
                cursor += 1
        if cursor == len(expected):
            return True, f"工具顺序符合：{' → '.join(expected)}"
        return False, f"工具顺序不符合，期望包含：{' → '.join(expected)}"

    if rule_type == "max_steps":
        limit = rule.get("value")
        passed = len(steps) <= limit
        detail = (
            f"{len(steps)} 步，未超过 {limit} 步"
            if passed
            else f"{len(steps)} 步，超过 {limit} 步"
        )
        return passed, detail

    if rule_type == "min_steps":
        limit = rule.get("value")
        passed = len(steps) >= limit
        return passed, f"{len(steps)} 步，下限 {limit} 步"

    if rule_type == "max_tool_calls":
        limit = rule.get("value")
        passed = len(actions) <= limit
        return passed, f"{len(actions)} 次工具调用，上限 {limit} 次"

    if rule_type == "forbidden_tool":
        tool = rule.get("tool")
        used = any(step.get("tool") == tool for step in actions)
        if used:
            return False, f"出现了禁止工具 {tool}"
        return True, f"未调用禁止工具 {tool}"

    if rule_type == "final_answer_contains":
        keyword = rule.get("value")
        answer = data.get("final_answer") or ""
        passed = keyword in answer
        if passed:
            return True, f"最终答案包含“{keyword}”"
        return False, f"最终答案未包含“{keyword}”"

    if rule_type == "no_error_steps":
        errors = [step for step in steps if step.get("type") == "error"]
        return (
            (False, f"存在 {len(errors)} 个 error 步骤")
            if errors
            else (True, "没有 error 步骤")
        )

    return False, f"未知规则：{rule_type}"
