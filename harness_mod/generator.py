import json
import time
from typing import Callable, Optional, Type, TypeVar

from pydantic import ValidationError

from schemas import TestScenarioSet

from .exceptions import HarnessError, RetryableLLMError
from .json_utils import extract_json
from .llm_client import call_llm_for_json
from .normalizers import normalize_test_case_values

T = TypeVar('T')
Normalizer = Optional[Callable[[dict], dict]]


def generate_with_retry(
    schema_cls: Type[T],
    system_prompt: str,
    user_prompt: str,
    max_retries: int = 2,
    normalizer: Normalizer = None,
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
            print(f'[WARN] attempt={attempt} failed: {e}')
            last_error = e
            time.sleep(2.0 * attempt)

    raise HarnessError(f'Failed after retries: {last_error}')
