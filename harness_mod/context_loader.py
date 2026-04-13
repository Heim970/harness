from pathlib import Path

IMPORTANT_KEYWORDS = ['Service', 'Repository', 'Controller', 'User', 'feature']
ALLOWED_SUFFIXES = {'.java', '.txt'}



def load_project_context(project_dir: str) -> str:
    """프로젝트 폴더를 읽어 컨텍스트에 추가"""
    base = Path(project_dir)
    parts: list[str] = []

    for path in sorted(base.rglob('*')):
        if not path.is_file():
            continue
        if path.suffix not in ALLOWED_SUFFIXES:
            continue
        if not any(keyword in path.name for keyword in IMPORTANT_KEYWORDS):
            continue

        content = path.read_text(encoding='utf-8')
        parts.append(f'\n[FILE: {path.name}]\n{content}')

    return '\n'.join(parts)
