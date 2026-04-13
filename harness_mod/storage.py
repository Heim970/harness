from pathlib import Path



def save_result(result, output_path: str) -> None:
    """LLM의 응답 결과를 json 파일로 저장"""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        result.model_dump_json(indent=2, ensure_ascii=False),
        encoding='utf-8',
    )
