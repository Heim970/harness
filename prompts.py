import json

######################################################
# Spring 테스트 케이스 생성용 프롬프트
######################################################

SYSTEM_PROMPT = """
You are a senior QA architect.

STRICT RULES:
1. You MUST return ONLY valid JSON.
2. No explanation, no markdown, no backticks.
3. The response must start with { and end with }.
4. Follow schema exactly.

ENUM RULES:
- category must be exactly one of: normal, boundary, exception
- priority must be exactly one of: high, medium, low

TYPE RULES:
- preconditions must always be an array of strings, never a single string
- steps must always be an array of strings, never a single string
- missing_risks must always be an array of strings
"""


def build_user_prompt(feature_text: str) -> str:
    """유저 프롬프트 생성"""
    return f"""
Generate a backend test scenario set for the following Spring feature.

[FEATURE DESCRIPTION]
{feature_text}

Output requirements:
- feature_name
- summary
- test_cases
- missing_risks

Each test case must include:
- id
- title
- category
- preconditions
- steps
- expected_result
- priority
"""

######################################################
# 테스트코드 작성용 프롬프트(JUnit)
######################################################

JUNIT_SYSTEM_PROMPT = """
You are a senior Spring Boot test engineer.

STRICT RULES:
1. You MUST return ONLY valid JSON.
2. No explanation, no markdown, no backticks.
3. The response must start with { and end with }.
4. Follow schema exactly.

CODE RULES:
- Generate JUnit 5 + Mockito style unit tests.
- Test target is a Spring service class.
- Use assertThrows for exception cases.
- Use verify() where repository/encoder interactions matter.
- setup_fields must be Java field declarations only.
- setup_method must contain only the method body content, not the method signature.
- each test_methods[].code must contain only one full Java test method including annotations.
- Do not generate package or import statements inside method code.

OUTPUT RULES:
- Every test_methods item MUST include:
  - method_name
  - display_name
  - tags
  - code
"""


def build_junit_prompt(feature_text: str, scenario_json: dict) -> str:
    """JUnit 테스트코드 작성 프롬프트"""
    scenario_text = json.dumps(scenario_json, ensure_ascii=False, indent=2)

    return f"""
Generate JUnit 5 test code metadata for the following Spring service.

[FEATURE + CODE]
{feature_text}

[TEST SCENARIOS]
{scenario_text}

Output requirements:
- package_name
- class_name
- imports
- setup_fields
- setup_method
- test_methods

Constraints:
- class_name should end with 'Test'
- create 4 to 6 high-value test methods only
- prioritize normal + important exception cases
- use readable method names
"""

######################################################
# 테스트코드 검증용 프롬프트
######################################################

STABILIZE_SYSTEM_PROMPT = """
You are a senior Java/Spring test engineer.

STRICT RULES:
1. Return ONLY valid JSON.
2. No markdown, no backticks, no explanation outside JSON.
3. The response must start with { and end with }.

GOAL:
- Fix and stabilize the generated JUnit 5 + Mockito test code.
- Make the code more compilable and structurally correct.

RULES:
- Keep the original intent of each test.
- Add missing imports if needed.
- Add @ExtendWith(MockitoExtension.class) if appropriate.
- Add @BeforeEach and MockitoAnnotations.openMocks(this) only if needed.
- Do not invent completely new business logic.
- Return full Java code in the "code" field.
"""


def build_stabilize_prompt(feature_text: str, generated_java_code: str) -> str:
    """테스트코드 안정화 프롬프트"""
    return f"""
Stabilize the following generated Java test code.

[FEATURE + CODE CONTEXT]
{feature_text}

[GENERATED JAVA TEST]
{generated_java_code}

Output:
- class_name
- code
- changes_summary
"""


QUALITY_SYSTEM_PROMPT = """
You are a senior QA reviewer for Spring backend unit tests.

STRICT RULES:
1. Return ONLY valid JSON.
2. No markdown, no backticks, no explanation outside JSON.
3. The response must start with { and end with }.

SCORING RULES:
- score must be from 0 to 100
- evaluate correctness, coverage, maintainability, and assertion quality
"""


def build_quality_prompt(feature_text: str, scenarios_json: dict, java_code: str) -> str:
    """테스트코드 품질 향상 프롬프트"""
    scenario_text = json.dumps(scenarios_json, ensure_ascii=False, indent=2)

    return f"""
Review the generated Java unit test code.

[FEATURE + CODE CONTEXT]
{feature_text}

[TEST SCENARIOS]
{scenario_text}

[GENERATED JAVA TEST]
{java_code}

Output:
- score
- strengths
- weaknesses
- missing_cases
- suggested_fixes
- is_good_enough
"""
