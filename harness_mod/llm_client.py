import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors

from .exceptions import RetryableLLMError

load_dotenv()

MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))


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
        response = _client.models.generate_content(
            model=MODEL,
            contents=contents,
            config={
                'temperature': 0.2,
            },
        )
        return response.text or ''

    except genai_errors.ServerError as e:
        raise RetryableLLMError(f'Server error: {e}') from e

    except genai_errors.ClientError as e:
        message = str(e)
        if '429' in message or 'RESOURCE_EXHAUSTED' in message:
            raise RetryableLLMError(f'Rate limit / quota error: {e}') from e
        raise

    except Exception as e:
        raise RetryableLLMError(f'Unexpected LLM call error: {e}') from e
