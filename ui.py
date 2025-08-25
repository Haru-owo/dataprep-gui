import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from llm_handler import LLMHandler
from prompt_creator import create_prompt
from config import MODEL_ID

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("모듈화된 LLM 데이터 전처리기 (Hugging Face 연동)")
        self.root.geometry("800x650")
        self.llm_handler = None
        self.setup_ui()
        self.initialize_model_async()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        options_frame = ttk.LabelFrame(main_frame, text="1. 전처리 옵션 선택", padding="10")
        options_frame.pack(fill=tk.X, pady=5)

        ttk.Label(options_frame, text="데이터 종류:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.data_type_var = tk.StringVar(value="비정형 (Text)")
        self.data_type_menu = ttk.Combobox(options_frame, textvariable=self.data_type_var, values=["비정형 (Text)", "반정형 (JSON)"], state="readonly")
        self.data_type_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.data_type_menu.bind("<<ComboboxSelected>>", self.update_task_options)

        ttk.Label(options_frame, text="작업 내용:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.task_var = tk.StringVar()
        self.task_menu = ttk.Combobox(options_frame, textvariable=self.task_var, state="readonly")
        self.task_menu.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(options_frame, text="추가 지시사항:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.instruction_var = tk.StringVar()
        self.instruction_entry = ttk.Entry(options_frame, textvariable=self.instruction_var)
        self.instruction_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        options_frame.columnconfigure(1, weight=1)

        input_frame = ttk.LabelFrame(main_frame, text="2. 원본 데이터 입력", padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=10)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        self.run_button = ttk.Button(main_frame, text="모델 로딩 중...", command=self.start_processing, state=tk.DISABLED)
        self.run_button.pack(fill=tk.X, pady=10)
        
        output_frame = ttk.LabelFrame(main_frame, text="3. 처리 결과", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=10, state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        self.update_task_options()

    def initialize_model_async(self):
        thread = threading.Thread(target=self.initialize_model)
        thread.start()

    def initialize_model(self):
        self.llm_handler = LLMHandler(MODEL_ID)
        if self.llm_handler.pipeline:
            self.root.after(0, self.on_model_loaded)
        else:
            self.root.after(0, self.on_model_load_failed)

    def on_model_loaded(self):
        self.run_button.config(text="✨ 전처리 실행 ✨", state=tk.NORMAL)
        messagebox.showinfo("완료", f"'{MODEL_ID}' 모델 로딩이 완료되었습니다.")

    def on_model_load_failed(self):
        self.run_button.config(text="모델 로딩 실패", state=tk.DISABLED)
        messagebox.showerror("오류", "모델 로딩에 실패했습니다. 환경 변수와 인터넷 연결을 확인해주세요.")

    def update_task_options(self, event=None):
        data_type = self.data_type_var.get()
        tasks = []
        if data_type == "비정형 (Text)":
            tasks = ["개인정보 비식별화 (Masking)", "핵심 키워드 추출", "텍스트 요약"]
        elif data_type == "반정형 (JSON)":
            tasks = ["원하는 정보 추출 (Key-Value)", "JSON 구조 평탄화 (Flatten)"]
        
        self.task_menu['values'] = tasks
        if tasks:
            self.task_var.set(tasks[0])

    def start_processing(self):
        self.run_button.config(state=tk.DISABLED, text="처리 중...")
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "LLM이 열심히 작업 중입니다...")
        self.output_text.config(state=tk.DISABLED)

        thread = threading.Thread(target=self.process_data)
        thread.start()

    def process_data(self):
        data_type = self.data_type_var.get()
        task = self.task_var.get()
        instruction = self.instruction_var.get()
        raw_data = self.input_text.get(1.0, tk.END).strip()

        if not raw_data:
            messagebox.showwarning("입력 오류", "원본 데이터를 입력해주세요.")
            self.root.after(0, self.update_ui_after_processing)
            return

        prompt = create_prompt(data_type, task, instruction, raw_data)
        result = self.llm_handler.get_response(prompt)
        self.root.after(0, self.update_ui_after_processing, result)

    def update_ui_after_processing(self, result=None):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        if result:
            self.output_text.insert(tk.END, result)
        self.output_text.config(state=tk.DISABLED)
        self.run_button.config(state=tk.NORMAL, text="✨ 전처리 실행 ✨")