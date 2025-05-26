# app.py
from flask import Flask, render_template, request, jsonify

app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)

# --- 기존 홈 라우트 (index.html 렌더링) ---
@app.route("/")
def calendar_page():
    return render_template("index.html")

# --- 일정 저장용 인-메모리 리스트 ---
_schedules = []

# --- schedules API 라우트 추가 ---
@app.route("/api/schedules", methods=["GET", "POST"])
def schedules_api():
    if request.method == "GET":
        return jsonify(_schedules), 200

    # POST 요청 처리
    data = request.get_json()
    # 최소 필수 필드 체크
    for field in ("start", "end", "city", "passengers"):
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    # 새 일정 객체 생성
    schedule = {
        "id": len(_schedules) + 1,
        "start": data["start"],
        "end": data["end"],
        "city": data["city"],
        "passengers": data["passengers"],
        "budget": data.get("budget", 0)
    }
    _schedules.append(schedule)
    return jsonify(schedule), 201

if __name__ == "__main__":
    app.run(debug=True)