import pypdf
import json

def read_file_content(file_path):
    """파일 경로를 받아 파일 종류에 맞게 텍스트를 추출합니다."""
    if file_path is None:
        return None, "파일 경로가 없습니다."

    try:
        if file_path.endswith('.pdf'):
            with open(file_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                text = "\n".join(page.extract_text() for page in reader.pages)
            return text, None
        elif file_path.endswith(('.txt', '.csv', '.xml')):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read(), None
        elif file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, indent=2, ensure_ascii=False), None
        else:
            # 지원하지 않는 파일은 오류 대신 None을 반환하여 건너뛰도록 합니다.
            return None, None
    except Exception as e:
        return None, f"파일을 읽는 중 오류가 발생했습니다: {e}"