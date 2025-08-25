def create_unstructured_semi_structured_prompt(custom_prompt, raw_data):
    """비정형/반정형 데이터 처리를 위한 프롬프트를 생성합니다."""
    prompt = f"""
[Instruction]
{custom_prompt}

[Data]
{raw_data}
"""
    return prompt

def create_structured_code_gen_prompt(task, column_info):
    """정형 데이터 처리 코드 생성을 위한 프롬프트를 생성합니다."""
    dataframe_name = "df" 

    task_instruction = ""
    if task == "결측치 정보 확인 (Info)":
        task_instruction = f"Display the summary information (using .info()) and the count of missing values for each column in the pandas DataFrame named '{dataframe_name}'."
    elif task == "특정 열(Column) 제거":
        task_instruction = f"Generate Python code to remove the column(s) named '{column_info}' from the pandas DataFrame named '{dataframe_name}'. The columns to drop are provided as a string, which might contain single or multiple column names separated by commas."
    elif task == "평균값으로 결측치 채우기":
        task_instruction = f"Generate Python code to fill the missing values in the numeric column(s) named '{column_info}' with their respective mean values. The columns are provided as a string, which might contain single or multiple column names separated by commas."
    elif task == "최빈값으로 결측치 채우기":
        task_instruction = f"Generate Python code to fill the missing values in the categorical column(s) named '{column_info}' with their respective mode (most frequent value). The columns are provided as a string, which might contain single or multiple column names separated by commas."

    prompt = f"""
You are an expert Python programmer specializing in data analysis with the pandas library.
Your task is to generate ONLY the Python code required to perform the following task.
Do not add any explanations, comments, `import pandas as pd`, or example usage. Just provide the raw, executable code snippet.

[Task]
{task_instruction}

[Code]
"""
    return prompt