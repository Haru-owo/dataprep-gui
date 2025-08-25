import gradio as gr
import tempfile
import os
import zipfile
from llm_handler import LLMHandler
from prompt_creator import create_prompt
from file_processor import read_file_content

print("모델을 로딩하고 있습니다... 시간이 걸릴 수 있습니다.")
try:
    llm_handler = LLMHandler()
    print("모델 로딩 완료!")
except (FileNotFoundError, ValueError, KeyError) as e:
    print(f"설정 오류: {e}")
    llm_handler = None

def process_folder(custom_prompt, folder_obj, save_format, progress=gr.Progress()):
    """폴더 내의 모든 파일을 처리하고 결과를 ZIP 파일로 묶는 로직"""
    if not folder_obj:
        return "폴더를 먼저 업로드해주세요.", None
    if not custom_prompt:
        return "프롬프트를 입력해주세요.", None
    if not llm_handler or not llm_handler.pipeline:
        return "모델이 로딩되지 않았습니다. setting.conf 파일을 확인하고 프로그램을 다시 시작해주세요.", None

    folder_path = folder_obj.name
    
    # 처리할 파일 목록 수집
    files_to_process = []
    for root, _, files in os.walk(folder_path):
        for name in files:
            files_to_process.append(os.path.join(root, name))

    if not files_to_process:
        return "폴더에 처리할 파일이 없습니다.", None
        
    processed_files = []
    total_files = len(files_to_process)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for i, file_path in enumerate(files_to_process):
            progress((i + 1) / total_files, desc=f"파일 처리 중... ({i+1}/{total_files}) {os.path.basename(file_path)}")
            
            raw_data, error = read_file_content(file_path)
            if error:
                print(f"파일 읽기 오류 ({os.path.basename(file_path)}): {error}")
                continue
            if raw_data is None: # 지원하지 않는 파일 형식
                continue

            prompt = create_prompt(custom_prompt, raw_data)
            result = llm_handler.get_response(prompt)
            
            original_filename = os.path.splitext(os.path.basename(file_path))[0]
            save_extension = f".{save_format}"
            result_filename = os.path.join(temp_dir, f"{original_filename}_processed{save_extension}")
            
            with open(result_filename, 'w', encoding='utf-8') as f:
                f.write(result)
            processed_files.append(result_filename)

        if not processed_files:
            return "처리된 파일이 없습니다. 지원하는 파일 형식이 맞는지 확인해주세요.", None
        
        progress(1.0, desc="결과 압축 중...")
        zip_path = tempfile.mktemp(suffix=".zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path in processed_files:
                zipf.write(file_path, arcname=os.path.basename(file_path))

    summary = f"총 {total_files}개 파일 중 {len(processed_files)}개를 성공적으로 처리했습니다."
    return summary, zip_path

# --- 프롬프트 레시피 ---
recipe_text_summary = "이 문서의 핵심 내용을 3가지 항목으로 요약해줘."
recipe_text_extract = "이 문서에서 언급된 모든 사람의 이름, 직책, 그리고 관련된 날짜를 찾아 목록으로 만들어줘."
recipe_semi_to_json = "이 데이터를 JSON 형식으로 변환해줘."
recipe_semi_to_csv = "이 데이터를 CSV 형식으로 변환해줘. 데이터의 첫 번째 줄을 헤더로 사용해줘."
recipe_semi_filter = "'status'가 'completed'이거나 'price'가 10000 이상인 항목만 추출해줘."

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 LLM 기반 데이터 전처리기 (v6)")
    gr.Markdown("폴더를 통째로 업로드하고, 원클릭 레시피나 직접 작성한 프롬프트로 데이터를 가공하세요.")

    with gr.Tabs():
        with gr.TabItem("비정형 데이터 (PDF, TXT)"):
            with gr.Row():
                with gr.Column(scale=1):
                    folder_upload_text = gr.File(label="PDF/TXT가 포함된 폴더 업로드", file_count="directory")
                    gr.Markdown("**원클릭 레시피**")
                    with gr.Row():
                        recipe_btn_t1 = gr.Button("핵심 요약")
                        recipe_btn_t2 = gr.Button("정보 추출")
                    prompt_tb_text = gr.Textbox(lines=8, label="프롬프트 엔지니어링", placeholder="처리할 내용을 직접 작성하거나, 원클릭 레시피를 사용하세요.")
                    save_format_text = gr.Dropdown(label="최종 저장 형식", choices=["txt", "json", "csv"], value="txt")
                with gr.Column(scale=2):
                    output_tb_text = gr.Textbox(lines=12, label="처리 결과 요약", interactive=False)
                    download_file_text = gr.File(label="결과 다운로드 (.zip)", interactive=False)
            
            run_button_text = gr.Button("✨ 텍스트 처리 실행 ✨", variant="primary")
            
            recipe_btn_t1.click(lambda: recipe_text_summary, outputs=prompt_tb_text)
            recipe_btn_t2.click(lambda: recipe_text_extract, outputs=prompt_tb_text)
            run_button_text.click(fn=process_folder, inputs=[prompt_tb_text, folder_upload_text, save_format_text], outputs=[output_tb_text, download_file_text], api_name="process_text_folder")

        with gr.TabItem("반정형 데이터 (JSON, CSV, XML)"):
            with gr.Row():
                with gr.Column(scale=1):
                    folder_upload_structured = gr.File(label="JSON/CSV/XML이 포함된 폴더 업로드", file_count="directory")
                    gr.Markdown("**원클릭 레시피**")
                    with gr.Row():
                        recipe_btn_s1 = gr.Button("JSON 변환")
                        recipe_btn_s2 = gr.Button("CSV 변환")
                    recipe_btn_s3 = gr.Button("조건 필터링 (예시)")
                    prompt_tb_structured = gr.Textbox(lines=8, label="프롬프트 엔지니어링", placeholder="처리할 내용을 직접 작성하거나, 원클릭 레시피를 사용하세요.")
                    save_format_structured = gr.Dropdown(label="최종 저장 형식", choices=["json", "csv", "txt"], value="json")
                with gr.Column(scale=2):
                    output_tb_structured = gr.Textbox(lines=12, label="처리 결과 요약", interactive=False)
                    download_file_structured = gr.File(label="결과 다운로드 (.zip)", interactive=False)
            
            run_button_structured = gr.Button("✨ 데이터 처리 실행 ✨", variant="primary")

            recipe_btn_s1.click(lambda: recipe_semi_to_json, outputs=prompt_tb_structured)
            recipe_btn_s2.click(lambda: recipe_semi_to_csv, outputs=prompt_tb_structured)
            recipe_btn_s3.click(lambda: recipe_semi_filter, outputs=prompt_tb_structured)
            run_button_structured.click(fn=process_folder, inputs=[prompt_tb_structured, folder_upload_structured, save_format_structured], outputs=[output_tb_structured, download_file_structured], api_name="process_structured_folder")

if __name__ == "__main__":
    if llm_handler:
        demo.launch()
    else:
        print("Gradio 앱을 시작할 수 없습니다. 설정 파일을 확인해주세요.")