import gradio as gr
from llm_handler import LLMHandler
from prompt_creator import create_prompt
from config import MODEL_ID

print("모델을 로딩하고 있습니다... 시간이 걸릴 수 있습니다.")
llm_handler = LLMHandler(MODEL_ID)
print("모델 로딩 완료!")

def process_data_with_prompt(custom_prompt, raw_data):
    """프롬프트 기반 데이터 처리 로직"""
    if not raw_data or not custom_prompt:
        return "프롬프트와 원본 데이터를 모두 입력해주세요."
    if not llm_handler or not llm_handler.pipeline:
        return "모델이 아직 로딩 중이거나 로딩에 실패했습니다. 잠시 후 다시 시도해주세요."

    prompt = create_prompt(custom_prompt, raw_data)
    result = llm_handler.get_response(prompt)
    return result

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 LLM 기반 데이터 전처리기 (Web UI)")
    gr.Markdown("처리할 데이터 종류에 맞는 탭을 선택하고, 자유로운 프롬프트로 데이터를 가공하세요.")

    with gr.Tabs():
        with gr.TabItem("비정형 데이터 (Text)"):
            gr.Markdown("### 일반 텍스트(기사, 리뷰, 이메일 등)를 처리합니다.")
            with gr.Row():
                with gr.Column(scale=1):
                    prompt_tb_text = gr.Textbox(
                        lines=10, 
                        label="프롬프트 엔지니어링", 
                        placeholder="처리할 내용을 자유롭게 작성해주세요.\n\n예시 (텍스트 요약):\n아래 내용을 세 문장으로 요약해줘.\n\n예시 (감성 분석):\n이 리뷰가 긍정적인지 부정적인지 판단해줘.\n\n예시 (정보 추출):\n여기서 언급된 사람 이름과 직책을 모두 뽑아줘."
                    )
                with gr.Column(scale=2):
                    input_tb_text = gr.Textbox(lines=10, label="원본 텍스트 데이터 입력", placeholder="여기에 처리할 텍스트를 붙여넣으세요...")
            
            run_button_text = gr.Button("✨ 텍스트 처리 실행 ✨", variant="primary")
            output_tb_text = gr.Textbox(lines=12, label="처리 결과", interactive=False)
            
            run_button_text.click(
                fn=process_data_with_prompt,
                inputs=[prompt_tb_text, input_tb_text],
                outputs=output_tb_text,
                api_name="process_text"
            )

        with gr.TabItem("반정형 데이터 (JSON/XML)"):
            gr.Markdown("### JSON, XML 등 구조를 가진 데이터를 처리합니다.")
            with gr.Row():
                with gr.Column(scale=1):
                    prompt_tb_json = gr.Textbox(
                        lines=10, 
                        label="프롬프트 엔지니어링", 
                        placeholder="처리할 내용을 자유롭게 작성해주세요.\n\n예시 (JSON -> CSV):\nJSON 데이터에서 'name'과 'email' 키 값만 추출해서 CSV 형식으로 만들어줘.\n\n예시 (XML -> JSON):\n아래 XML 데이터를 JSON 형식으로 변환해줘.\n\n예시 (데이터 필터링):\n'age'가 30 이상인 사용자 데이터만 추출해줘."
                    )
                with gr.Column(scale=2):
                    input_tb_json = gr.Textbox(lines=10, label="원본 JSON/XML 데이터 입력", placeholder="여기에 처리할 데이터를 붙여넣으세요...")

            run_button_json = gr.Button("✨ 데이터 처리 실행 ✨", variant="primary")
            output_tb_json = gr.Textbox(lines=12, label="처리 결과", interactive=False)
            
            run_button_json.click(
                fn=process_data_with_prompt,
                inputs=[prompt_tb_json, input_tb_json],
                outputs=output_tb_json,
                api_name="process_semi_structured"
            )

if __name__ == "__main__":
    demo.launch()