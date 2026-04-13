# main.py
import argparse
from pathlib import Path

from harness import (
    run,
    run_junit_generation,
    run_java_stabilization,
    run_quality_check,
    save_result,
    render_junit_java,
    load_project_context,
)


def main():
    # =========================================================
    # 0. CLI 인자 파싱
    # - command: 실행할 작업 (현재는 run만 지원)
    # - project_dir: 분석 대상 프로젝트 경로
    # - --out: 결과 저장 루트 디렉토리
    # - --name: 실행 결과를 구분하기 위한 하위 폴더명
    # =========================================================
    parser = argparse.ArgumentParser(description="LLM 기반 테스트 생성 harness")
    parser.add_argument("command", help="run")
    parser.add_argument("project_dir", help="target project directory")
    parser.add_argument("--out", default="outputs", help="output base directory")
    parser.add_argument("--name", default="run1", help="execution name (subfolder)")

    args = parser.parse_args()

    # =========================================================
    # 1. 실행 디렉토리 준비
    # - outputs/<name>/ 구조로 결과를 분리 저장
    # - 실험/버전별 결과 비교 가능
    # =========================================================
    out_dir = Path(args.out) / args.name
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.command == "run":
        # =====================================================
        # 2. 프로젝트 컨텍스트 로딩
        # - Java 소스 및 텍스트 파일을 수집
        # - LLM 입력용 하나의 문자열로 결합
        # =====================================================
        combined = load_project_context(args.project_dir)

        # =====================================================
        # 3. 테스트 시나리오 생성
        # - 기능 + 코드 기반으로 테스트 케이스(JSON) 생성
        # =====================================================
        scenario = run(combined)
        save_result(scenario, out_dir / "test_scenarios.json")

        # =====================================================
        # 4. JUnit 테스트 메타데이터 생성
        # - 시나리오를 기반으로 테스트 코드 구조(JSON) 생성
        # =====================================================
        junit = run_junit_generation(combined, scenario)
        save_result(junit, out_dir / "generated_junit_test.json")

        # =====================================================
        # 5. Java 테스트 코드 렌더링
        # - JSON → 실제 JUnit Java 코드로 변환
        # =====================================================
        code = render_junit_java(junit)
        (out_dir / "UserServiceTest.java").write_text(code, encoding="utf-8")

        # =====================================================
        # 6. 테스트 코드 안정화
        # - import, annotation, 구조 보완
        # - 컴파일 가능성 및 일관성 향상
        # =====================================================
        stabilized = run_java_stabilization(combined, code)
        save_result(stabilized, out_dir / "stabilized.json")

        (out_dir / "UserServiceTest.stabilized.java").write_text(
            stabilized.code, encoding="utf-8"
        )

        # =====================================================
        # 7. 테스트 품질 검증
        # - 커버리지, assertion 품질, 누락 케이스 평가
        # - 점수 및 개선 제안 리포트 생성
        # =====================================================
        quality = run_quality_check(combined, scenario, stabilized.code)
        save_result(quality, out_dir / "quality.json")

        # =====================================================
        # 8. 결과 요약 출력
        # =====================================================
        print("\n=== RESULT SUMMARY ===")
        print(f"Output directory: {out_dir}")
        print(f"Quality Score   : {quality.score}")
        print(f"Good Enough     : {quality.is_good_enough}")


if __name__ == "__main__":
    main()
