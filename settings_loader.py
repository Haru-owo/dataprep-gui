import configparser

def load_settings():
    """setting.conf 파일에서 설정을 읽어옵니다."""
    config = configparser.ConfigParser()
    try:
        if not config.read('setting.conf'):
            raise FileNotFoundError("setting.conf 파일을 찾을 수 없습니다. 파일을 생성하고 내용을 채워주세요.")
        
        settings = {
            'hf_token': config.get('HUGGINGFACE', 'TOKEN'),
            'model_id': config.get('HUGGINGFACE', 'MODEL_ID')
        }
        
        if not settings['hf_token'] or "여기에" in settings['hf_token']:
             raise ValueError("setting.conf 파일에 유효한 허깅페이스 TOKEN을 입력해주세요.")

        return settings
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        raise KeyError(f"setting.conf 파일에 필요한 설정이 없습니다: {e}")