# talk2travel/services/local_parser.py

import json
from transformers import AutoTokenizer, AutoModelForCausalLM, TextGenerationPipeline

MODEL_NAME = "EleutherAI/gpt-neo-125M"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model     = AutoModelForCausalLM.from_pretrained(MODEL_NAME, device_map="auto")
pipe      = TextGenerationPipeline(model=model, tokenizer=tokenizer, return_full_text=False)

def parse_trip_local(user_text: str) -> dict:
    """
    작은 모델에 few-shot 예시를 주고, 오직 JSON만 출력하도록 강제합니다.
    """
    prompt = f"""
다음 예시를 보고, 여행 요청을 **엄격히** JSON 형식으로만 변환하세요.
출력할 키: city, start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), pax (정수), budget (숫자)

예시 1:
Input: "7월 3일부터 7월 7일까지 오사카 2인 여행, 예산 천 달러"
Output: {{"city":"Osaka","start_date":"2025-07-03","end_date":"2025-07-07","pax":2,"budget":1000}}

예시 2:
Input: "6월 10-15일 파리 3명 2000유로"
Output: {{"city":"Paris","start_date":"2025-06-10","end_date":"2025-06-15","pax":3,"budget":2000}}

이제 아래 여행 요청을 같은 규칙으로 처리하세요.

Input: "{user_text}"
Output:
"""
    outputs = pipe(prompt, max_new_tokens=128, do_sample=False)
    gen = outputs[0]["generated_text"].strip()

    # JSON 부분만 추출
    start = gen.find("{")
    end   = gen.rfind("}") + 1
    json_str = gen[start:end] if start != -1 and end != -1 else gen

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {
            "city": None,
            "start_date": None,
            "end_date": None,
            "pax": None,
            "budget": None
        }
