def normalize_test_case_values(data: dict) -> dict:
    """테스트 시나리오 응답 정규화"""
    category_map = {
        'positive': 'normal',
        'normal': 'normal',
        'boundary': 'boundary',
        'positive / edge': 'boundary',
        'edge': 'boundary',
        'negative': 'exception',
        'exception': 'exception',
        'negative / boundary': 'exception',
    }

    priority_map = {
        'high': 'high',
        'medium': 'medium',
        'low': 'low',
    }

    if 'test_cases' not in data or not isinstance(data['test_cases'], list):
        return data

    for tc in data['test_cases']:
        if not isinstance(tc, dict):
            continue

        raw_category = str(tc.get('category', '')).strip().lower()
        raw_priority = str(tc.get('priority', '')).strip().lower()

        if raw_category in category_map:
            tc['category'] = category_map[raw_category]

        if raw_priority in priority_map:
            tc['priority'] = priority_map[raw_priority]

        preconditions = tc.get('preconditions')
        if isinstance(preconditions, str):
            text = preconditions.strip()
            if text.lower() in {'none', 'none.', '없음', '없음.'}:
                tc['preconditions'] = []
            elif text:
                tc['preconditions'] = [text]
            else:
                tc['preconditions'] = []

        steps = tc.get('steps')
        if isinstance(steps, str):
            text = steps.strip()
            tc['steps'] = [text] if text else []

    return data


def normalize_junit_result(data: dict) -> dict:
    """JUnit 테스트 코드 정규화"""
    if 'imports' in data and isinstance(data['imports'], str):
        data['imports'] = [data['imports']]

    if 'setup_fields' in data and isinstance(data['setup_fields'], str):
        data['setup_fields'] = [data['setup_fields']]

    if 'test_methods' not in data or not isinstance(data['test_methods'], list):
        data['test_methods'] = []

    for i, tm in enumerate(data['test_methods']):
        if not isinstance(tm, dict):
            continue

        code = tm.get('code', '')
        method_name = None

        for line in code.splitlines():
            stripped = line.strip()
            if stripped.startswith('void '):
                method_name = stripped.replace('void', '').split('(')[0].strip()
                break

        if not method_name:
            method_name = f'test_method_{i}'

        tm['method_name'] = tm.get('method_name') or method_name
        tm['display_name'] = tm.get('display_name') or method_name

        tags = tm.get('tags')
        if isinstance(tags, str):
            tm['tags'] = [tags]
        elif tags is None:
            tm['tags'] = []

    return data


def normalize_stabilized_java_result(data: dict) -> dict:
    """생성된 자바 코드 summary 형식 정규화"""
    if 'changes_summary' in data and isinstance(data['changes_summary'], str):
        data['changes_summary'] = [data['changes_summary']]
    elif 'changes_summary' not in data:
        data['changes_summary'] = []

    return data


def normalize_quality_result(data: dict) -> dict:
    """생성된 자바 코드 품질 결과 정규화"""
    for key in ['strengths', 'weaknesses', 'missing_cases', 'suggested_fixes']:
        if key in data and isinstance(data[key], str):
            data[key] = [data[key]]
        elif key not in data:
            data[key] = []

    if 'is_good_enough' not in data:
        score = int(data.get('score', 0))
        data['is_good_enough'] = score >= 70

    return data
