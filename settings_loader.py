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


# ----------------------------------------------------
# 파일 3: llm_handler.py
# - 허깅페이스 모델을 불러오고 응답을 생성하는 파일입니다. (수정됨)
# ----------------------------------------------------
import torch
from transformers import pipeline
from settings_loader import load_settings

class LLMHandler:
    # __init__ 생성자가 이제 아무 인자도 받지 않습니다.
    def __init__(self):
        self.settings = load_settings()
        self.model_id = self.settings['model_id']
        self.hf_token = self.settings['hf_token']
        self.pipeline = None
        self._initialize_pipeline()

    def _initialize_pipeline(self):
        try:
            self.pipeline = pipeline(
                "text-generation",
                model=self.model_id,
                model_kwargs={"torch_dtype": torch.bfloat16},
                device_map="auto",
                token=self.hf_token
            )
        except Exception as e:
            print(f"모델 파이프라인 초기화 중 오류 발생: {e}")
            self.pipeline = None

    def get_response(self, prompt):
        if not self.pipeline:
            return "모델이 초기화되지 않았습니다. 설정을 확인해주세요."

        messages = [
            {"role": "system", "content": "You are a highly skilled data processing expert. Provide only the processed result without any additional explanation or conversation."},
            {"role": "user", "content": prompt},
        ]
        
        terminators = [
            self.pipeline.tokenizer.eos_token_id,
            self.pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        try:
            outputs = self.pipeline(
                messages,
                max_new_tokens=1024,
                eos_token_id=terminators,
                do_sample=True,
                temperature=0.6,
                top_p=0.9,
            )
            response = outputs[0]["generated_text"][-1]["content"]
            return response.strip()
        except Exception as e:
            return f"응답 생성 중 오류 발생: {e}"