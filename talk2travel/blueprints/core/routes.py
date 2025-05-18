from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask import current_app
from talk2travel.blueprints.api.routes import parse_request

core_bp = Blueprint("core", __name__)

@core_bp.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        user_text = request.form.get("text")

        # 내부 API(parse_request) 직접 호출
        # 테스트 컨텍스트를 만들어서 POST /api/parse 를 시뮬레이션합니다.
        with current_app.test_request_context(
                "/api/parse",
                method="POST",
                json={"text": user_text}
        ):
            response = parse_request()        # Flask Response 객체
        data = response.get_json()            # 파싱된 dict

        return render_template("results.html", parsed=data)

    return render_template("home.html")
