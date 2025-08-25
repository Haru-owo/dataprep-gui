def create_prompt(custom_prompt, raw_data, output_format):
    """데이터 처리를 위한 프롬프트를 생성합니다."""
    prompt = f"""
[Instruction]
{custom_prompt}

[Data]
{raw_data}

[Output Format]
Please format your final response strictly as {output_format}.
"""
    return prompt