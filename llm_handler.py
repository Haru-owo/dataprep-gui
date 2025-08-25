import torch
from transformers import pipeline
from settings_loader import load_settings

class LLMHandler:
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