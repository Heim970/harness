class HarnessError(Exception):
    """Harness 실행 중 발생하는 예외"""


class RetryableLLMError(Exception):
    """
    재시도 대상 예외
    - 429: Rate limit / quota error
    - 5xx: 서버 과부하, 일시 장애
    """
