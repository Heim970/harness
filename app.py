from pathlib import Path
from harness import (
    run,
    run_junit_generation,
    run_java_stabilization,
    run_quality_check,
    save_result,
    render_junit_java,
)

if __name__ == "__main__":
    feature_text = Path("samples/feature.txt").read_text(encoding="utf-8")
    code_text = Path("samples/service.java").read_text(encoding="utf-8")

    COMBINED_INPUT = f"""
{feature_text}

[CODE]
{code_text}
"""

    # 1) 테스트 시나리오 생성
    scenario_result = run(COMBINED_INPUT)
    save_result(scenario_result, "outputs/test_scenarios.json")
    print("Saved to outputs/test_scenarios.json")

    # 2) JUnit 메타 생성
    junit_result = run_junit_generation(COMBINED_INPUT, scenario_result)
    save_result(junit_result, "outputs/generated_junit_test.json")
    print("Saved to outputs/generated_junit_test.json")

    # 3) JUnit Java 렌더링
    JAVA_CODE = render_junit_java(junit_result)
    Path("outputs/UserServiceTest.java").write_text(JAVA_CODE, encoding="utf-8")
    print("Saved to outputs/UserServiceTest.java")

    # 4) Java 안정화
    stabilized_result = run_java_stabilization(COMBINED_INPUT, JAVA_CODE)
    save_result(stabilized_result, "outputs/stabilized_junit_test.json")
    Path("outputs/UserServiceTest.stabilized.java").write_text(
        stabilized_result.code,
        encoding="utf-8"
    )
    print("Saved to outputs/stabilized_junit_test.json")
    print("Saved to outputs/UserServiceTest.stabilized.java")

    # 5) 품질 검증
    quality_result = run_quality_check(
        COMBINED_INPUT,
        scenario_result,
        stabilized_result.code,
    )
    save_result(quality_result, "outputs/test_quality_report.json")
    print("Saved to outputs/test_quality_report.json")

    print("=== QUALITY SCORE ===")
    print(quality_result.score)
    print("=== GOOD ENOUGH ===")
    print(quality_result.is_good_enough)
