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

from .generator import generate_with_retry
from .normalizers import (
    normalize_junit_result,
    normalize_stabilized_java_result,
    normalize_quality_result,
)


def run(feature_text: str) -> TestScenarioSet:
    """테스트 시나리오 생성"""
    user_prompt = build_user_prompt(feature_text)
    return generate_with_retry(
        schema_cls=TestScenarioSet,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_retries=2,
    )



def run_junit_generation(
    feature_text: str,
    scenario_result: TestScenarioSet,
) -> GeneratedJUnitTest:
    """JUnit 테스트코드 생성"""
    user_prompt = build_junit_prompt(
        feature_text=feature_text,
        scenario_json=scenario_result.model_dump(),
    )

    return generate_with_retry(
        schema_cls=GeneratedJUnitTest,
        system_prompt=JUNIT_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_retries=2,
        normalizer=normalize_junit_result,
    )



def run_java_stabilization(feature_text: str, java_code: str) -> StabilizedJavaTest:
    """생성된 자바 코드 검증 실행"""
    user_prompt = build_stabilize_prompt(feature_text, java_code)

    return generate_with_retry(
        schema_cls=StabilizedJavaTest,
        system_prompt=STABILIZE_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_retries=3,
        normalizer=normalize_stabilized_java_result,
    )



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

    return generate_with_retry(
        schema_cls=QualityCheckResult,
        system_prompt=QUALITY_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_retries=3,
        normalizer=normalize_quality_result,
    )
