import json
import os.path
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent
JSON_FILE = os.path.join(BASE_DIR,'login_info.json')

def get_login_info(
        key: str,
        default_value: Optional[str] = None,
        json_path : str = JSON_FILE
):
    # Json 파일 읽어온 후, 변수에 저장
    with open(json_path) as f :
        secret_data = f.read()

    # 추출한 Json 파일, dict 형으로 형 변환
    secret_data = json.loads(secret_data)

    try:
        secret_data
    except:
        if default_value :
            return default_value

        raise EnvironmentError(f'Set the {key} environment variable')
