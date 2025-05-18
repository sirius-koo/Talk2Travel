import os
import json
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from talk2travel.services.local_parser import parse_trip_local

# .env 파일 로딩
load_dotenv()

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/parse", methods=["POST"])
def parse_request():
    """
    POST /api/parse
    Body: { "text": "<자연어 여행 요청>" }

    gpt-neo-125M 로컬 모델로만 파싱하여
    { city, start_date, end_date, pax, budget } 형태로 반환합니다.
    """
    data = request.get_json(force=True)
    user_text = data.get("text", "").strip()
    if not user_text:
        return jsonify({"error": "text 필드가 필요합니다."}), 400

    # 로컬 모델을 이용한 파싱
    parsed = parse_trip_local(user_text)

    return jsonify(parsed)