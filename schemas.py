from pydantic import BaseModel, Field
from typing import List, Literal


class TestCase(BaseModel):
    id: str = Field(description="TC ID, e.g. TC-001")
    title: str
    category: Literal["normal", "boundary", "exception"]
    preconditions: List[str]
    steps: List[str]
    expected_result: str
    priority: Literal["high", "medium", "low"]


class TestScenarioSet(BaseModel):
    feature_name: str
    summary: str
    test_cases: List[TestCase]
    missing_risks: List[str] = []


class GeneratedTestMethod(BaseModel):
    method_name: str
    display_name: str
    tags: List[str]
    code: str


class GeneratedJUnitTest(BaseModel):
    package_name: str
    class_name: str
    imports: List[str]
    setup_fields: List[str]
    setup_method: str
    test_methods: List[GeneratedTestMethod]


class StabilizedJavaTest(BaseModel):
    class_name: str
    code: str
    changes_summary: List[str]


class QualityCheckResult(BaseModel):
    score: int = Field(ge=0, le=100)
    strengths: List[str]
    weaknesses: List[str]
    missing_cases: List[str]
    suggested_fixes: List[str]
    is_good_enough: bool
