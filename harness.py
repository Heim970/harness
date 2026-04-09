import os
import json
import time
from pathlib import Path
from typing import Type, TypeVar

from google import genai
from google.genai import errors as genai_errors

from pydantic import ValidationError
from dotenv import load_dotenv

from prompts import (
    SYSTEM_PROMPT,
    build_user_prompt,
    JUNIT_SYSTEM_PROMPT,
    build_junit_prompt,
    STABILIZE_SYSTEM_PROMPT,
    build_stabilize_prompt,
    QUALITY_SYSTEM_PROMPT,
    build_quality_prompt,
)

from schemas import (
    TestScenarioSet,
    GeneratedJUnitTest,
    StabilizedJavaTest,
    QualityCheckResult,
)

load_dotenv()

T = TypeVar("T")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


class HarnessError(Exception):
    """Harness 실행 중 발생하는 예외"""


class RetryableLLMError(Exception):
    """
    재시도 대상 예외
    - 429: Rate limit / quota error
    - 5xx: 서버 과부하, 일시 장애
    """


def call_llm_for_json(system_prompt: str, user_prompt: str) -> str:
    """
    LLM을 호출
    - 입력: json
    - 출력: json
    """
    contents = f"""
[SYSTEM]
{system_prompt}

[USER]
{user_prompt}
"""
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config={
                "temperature": 0.2,
            }
        )
        return response.text or ""

    except genai_errors.ServerError as e:
        # 5xx: 서버 과부하, 일시 장애 -> 재시도 대상
        raise RetryableLLMError(f"Server error: {e}") from e

    except genai_errors.ClientError as e:
        # 429: 재시도 대상
        message = str(e)
        if "429" in message or "RESOURCE_EXHAUSTED" in message:
            raise RetryableLLMError(f"Rate limit / quota error: {e}") from e
        raise

    except Exception as e:
        # 연결 불안정, 타임아웃 등도 일단 재시도
        raise RetryableLLMError(f"Unexpected LLM call error: {e}") from e


def generate_with_retry(
    schema_cls: Type[T],
    system_prompt: str,
    user_prompt: str,
    max_retries: int = 2,
    normalizer=None,
) -> T:
    """LLM 응답 생성과 실패 시 재시도"""
    last_error = None

    for attempt in range(1, max_retries + 2):
        try:
            raw = call_llm_for_json(system_prompt, user_prompt)

            json_text = extract_json(raw)
            data = json.loads(json_text)

            if schema_cls is TestScenarioSet:
                data = normalize_test_case_values(data)

            if normalizer is not None:
                data = normalizer(data)

            return schema_cls.model_validate(data)

        except (RetryableLLMError, json.JSONDecodeError, ValidationError) as e:
            print(f"[WARN] attempt={attempt} failed: {e}")
            last_error = e
            time.sleep(2.0 * attempt)

    raise HarnessError(f"Failed after retries: {last_error}")


def save_result(result: TestScenarioSet, output_path: str) -> None:
    """LLM의 응답 결과를 json 파일로 저장"""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        result.model_dump_json(indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def run(feature_text: str) -> TestScenarioSet:
    """LLM 실행"""
    user_prompt = build_user_prompt(feature_text)
    result = generate_with_retry(
        schema_cls=TestScenarioSet,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_retries=2
    )
    return result


def extract_json(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}") + 1
    return text[start:end]


def normalize_test_case_values(data: dict) -> dict:
    """harness.py에 파싱 전에 정규화"""
    category_map = {
        "positive": "normal",
        "normal": "normal",
        "boundary": "boundary",
        "positive / edge": "boundary",
        "edge": "boundary",
        "negative": "exception",
        "exception": "exception",
        "negative / boundary": "exception",
    }

    priority_map = {
        "high": "high",
        "medium": "medium",
        "low": "low",
    }

    if "test_cases" not in data or not isinstance(data["test_cases"], list):
        return data

    for tc in data["test_cases"]:
        if not isinstance(tc, dict):
            continue

        raw_category = str(tc.get("category", "")).strip().lower()
        raw_priority = str(tc.get("priority", "")).strip().lower()

        if raw_category in category_map:
            tc["category"] = category_map[raw_category]

        if raw_priority in priority_map:
            tc["priority"] = priority_map[raw_priority]

        # preconditions: str -> List[str]
        preconditions = tc.get("preconditions")
        if isinstance(preconditions, str):
            text = preconditions.strip()
            if text.lower() in {"none", "none.", "없음", "없음."}:
                tc["preconditions"] = []
            elif text:
                tc["preconditions"] = [text]
            else:
                tc["preconditions"] = []

        # step: 문자열로 오는 경우 대비
        steps = tc.get("steps")
        if isinstance(steps, str):
            text = steps.strip()
            tc["steps"] = [text] if text else []

    return data


def normalize_junit_result(data: dict) -> dict:
    """JUnit 테스트 코드 정규화"""
    if "imports" in data and isinstance(data["imports"], str):
        data["imports"] = [data["imports"]]

    if "setup_fields" in data and isinstance(data["setup_fields"], str):
        data["setup_fields"] = [data["setup_fields"]]

    if "test_methods" not in data or not isinstance(data["test_methods"], list):
        data["test_methods"] = []

    for i, tm in enumerate(data["test_methods"]):
        if not isinstance(tm, dict):
            continue

        # code에서 method 이름 추출
        code = tm.get("code", "")

        method_name = None

        for line in code.splitlines():
            line = line.strip()
            if line.startswith("void "):
                method_name = line.replace("void", "").split("(")[0].strip()
                break

        # fallback
        if not method_name:
            method_name = f"test_method_{i}"

        # 보정
        tm["method_name"] = tm.get("method_name") or method_name
        tm["display_name"] = tm.get("display_name") or method_name

        # tags 보정
        tags = tm.get("tags")
        if isinstance(tags, str):
            tm["tags"] = [tags]
        elif tags is None:
            tm["tags"] = []

    return data


def run_junit_generation(feature_text: str, scenario_result: TestScenarioSet) -> GeneratedJUnitTest:
    """JUnit 테스트코드 생성"""
    user_prompt = build_junit_prompt(
        feature_text=feature_text,
        scenario_json=scenario_result.model_dump()
    )

    result = generate_with_retry(
        schema_cls=GeneratedJUnitTest,
        system_prompt=JUNIT_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_retries=2,
        normalizer=normalize_junit_result,
    )
    return result


def render_junit_java(result: GeneratedJUnitTest) -> str:
    lines = []

    if result.package_name:
        lines.append(f"package {result.package_name};")
        lines.append("")

    for imp in result.imports:
        lines.append(f"import {imp};")
    lines.append("")

    lines.append(f"class {result.class_name} " + "{")

    for field in result.setup_fields:
        lines.append(f"    {field}")
    lines.append("")

    lines.append("    @BeforeEach")
    lines.append("    void setUp() {")
    for line in result.setup_method.splitlines():
        lines.append(f"        {line}")
    lines.append("    }")
    lines.append("")

    for method in result.test_methods:
        for line in method.code.splitlines():
            lines.append(f"    {line}")
        lines.append("")

    lines.append("}")

    return "\n".join(lines)


def normalize_stabilized_java_result(data: dict) -> dict:
    """생성된 자바 코드(JUnit test code)의 summary 형식 정규화"""
    if "changes_summary" in data and isinstance(data["changes_summary"], str):
        data["changes_summary"] = [data["changes_summary"]]
    elif "changes_summary" not in data:
        data["changes_summary"] = []

    return data


def normalize_quality_result(data: dict) -> dict:
    """생성된 자바 코드(JUnit test code)의 에러 케이스 및 품질점수 정규화"""
    for key in ["strengths", "weaknesses", "missing_cases", "suggested_fixes"]:
        if key in data and isinstance(data[key], str):
            data[key] = [data[key]]
        elif key not in data:
            data[key] = []

    if "is_good_enough" not in data:
        score = int(data.get("score", 0))
        data["is_good_enough"] = score >= 70

    return data


def run_java_stabilization(feature_text: str, java_code: str) -> StabilizedJavaTest:
    """생성된 자바 코드 검증 실행"""
    user_prompt = build_stabilize_prompt(feature_text, java_code)

    result = generate_with_retry(
        schema_cls=StabilizedJavaTest,
        system_prompt=STABILIZE_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_retries=3,
        normalizer=normalize_stabilized_java_result,
    )
    return result


def run_quality_check(
    feature_text: str,
    scenario_result: TestScenarioSet,
    java_code: str,
) -> QualityCheckResult:
    """생성된 자바 코드의 품질 검수"""
    user_prompt = build_quality_prompt(
        feature_text=feature_text,
        scenarios_json=scenario_result.model_dump(),
        java_code=java_code,
    )

    result = generate_with_retry(
        schema_cls=QualityCheckResult,
        system_prompt=QUALITY_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_retries=3,
        normalizer=normalize_quality_result,
    )
    return result
