from datetime import datetime, date
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid, click
from config import Config
from amadeus import Client, ResponseError
from sqlalchemy import or_

amadeus = Client(
    client_id=Config.AMADEUS_CLIENT_ID,
    client_secret=Config.AMADEUS_CLIENT_SECRET
)

app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)

# ── Database 설정 ─────────────────────────────────
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///schedules.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ── ERD 기반 모델 정의 ───────────────────────────────
# User
class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.String(36), primary_key=True)  # UUID로 생성할 수도 있고
    email         = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    payment_methods = db.relationship("PaymentMethod", back_populates="user")

# Schedule
class Schedule(db.Model):
    __tablename__ = "schedules"   # ERD의 TRIP 테이블

    id                = db.Column(db.String(36), primary_key=True)
    user_id           = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    start_date        = db.Column(db.Date,   nullable=False)
    end_date          = db.Column(db.Date,   nullable=False)
    departure_airport = db.Column(db.String(100), nullable=False)
    arrival_airport   = db.Column(db.String(10), nullable=True)
    passengers        = db.Column(db.Integer,    nullable=False)
    budget            = db.Column(db.Numeric(10,2), nullable=True)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at        = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    transactions = db.relationship("PaymentTransaction", back_populates="trip")

# PaymentMethod
class PaymentMethod(db.Model):
    __tablename__ = "payment_methods"

    id           = db.Column(db.String(36), primary_key=True)
    user_id      = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    payment_type = db.Column(db.String(50), nullable=False)
    provider     = db.Column(db.String(50), nullable=False)
    token        = db.Column(db.String(200), nullable=False)
    card_last4   = db.Column(db.String(4), nullable=False)
    exp_month    = db.Column(db.Integer, nullable=False)
    exp_year     = db.Column(db.Integer, nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user         = db.relationship("User", back_populates="payment_methods")
    transactions = db.relationship("PaymentTransaction", back_populates="payment_method")

# PaymentTransaction
class PaymentTransaction(db.Model):
    __tablename__ = "payment_transactions"

    id                = db.Column(db.String(36), primary_key=True)
    trip_id           = db.Column(db.Integer, db.ForeignKey("schedules.id"), nullable=False)
    payment_method_id = db.Column(db.String(36), db.ForeignKey("payment_methods.id"), nullable=False)
    amount            = db.Column(db.Numeric(10,2), nullable=False)
    currency          = db.Column(db.String(3), nullable=False)
    payment_status    = db.Column(db.String(20), nullable=False)
    transaction_id    = db.Column(db.String(100), nullable=False)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at        = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    trip              = db.relationship("Schedule", back_populates="transactions")
    payment_method    = db.relationship("PaymentMethod", back_populates="transactions")

# Aorport Code
class Airport(db.Model):
    __tablename__ = "airports"

    iata_code = db.Column(db.String(3), primary_key=True)
    icao_code = db.Column(db.String(4))
    name_en   = db.Column(db.String(100), nullable=False)
    name_ko   = db.Column(db.String(100))
    region    = db.Column(db.String(100))
    country_en= db.Column(db.String(100))
    country_ko= db.Column(db.String(100))
    city_en   = db.Column(db.String(100))

# ────────────────────────────────────────────────────────
@app.cli.command("init-db")
def init_db():
    """데이터베이스와 테이블을 초기화합니다."""
    # 앱 컨텍스트 없이도 작동하도록, 내부에서 create_all 호출
    db.create_all()
    click.echo("Initialized the database.")

# ── 뷰 및 API 라우트 ─────────────────────────────────
@app.route("/")
def calendar_page():
    return render_template("index.html")


@app.route("/api/schedules", methods=["GET", "POST"])
def schedules_api():
    if request.method == "GET":
        schedules = Schedule.query.all()
        return jsonify([
            {
                "id":         s.id,
                "user_id":    s.user_id,
                "start":      s.start_date.isoformat(),
                "end":        s.end_date.isoformat(),
                "departure_airport":  s.departure_airport,
                "arrival_airport":    s.arrival_airport,
                "passengers": s.passengers,
                "budget":     float(s.budget) if s.budget is not None else None
            }
            for s in schedules
        ]), 200

    data = request.get_json()
    # 필수 필드 검증
    for field in ("user_id", "start", "end", "departure_airport", "arrival_airport", "passengers"):
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    # 문자열 → date 객체 변환
    try:
        start_dt = date.fromisoformat(data["start"])
        end_dt   = date.fromisoformat(data["end"])
    except ValueError:
        return jsonify({"error": "Invalid date format, expected YYYY-MM-DD"}), 400

    # 타입 캐스팅
    try:
        passengers = int(data["passengers"])
    except ValueError:
        return jsonify({"error": "Invalid passengers, integer required"}), 400

    budget = data.get("budget")
    if budget is not None:
        try:
            budget = float(budget)
        except ValueError:
            return jsonify({"error": "Invalid budget, number required"}), 400

    # 새 Schedule 생성 (UUID PK)
    sched = Schedule(
        id         = str(uuid.uuid4()),
        user_id    = data["user_id"],
        start_date = start_dt,
        end_date   = end_dt,
        departure_airport = data["departure_airport"],
        arrival_airport   = data["arrival_airport"],
        passengers = passengers,
        budget     = budget
    )
    db.session.add(sched)
    db.session.commit()

    return jsonify({
        "id":         sched.id,
        "user_id":    sched.user_id,
        "start":      sched.start_date.isoformat(),
        "end":        sched.end_date.isoformat(),
        "departure_airport": sched.departure_airport,
        "arrival_airport":   sched.arrival_airport,
        "passengers": sched.passengers,
        "budget":     sched.budget
    }), 201

@app.route("/api/airports")
def airports_api():
    """
    ?city=키워드 로 호출하면
    city_en, name_en, name_ko 에 부분일치하는 공항 최대 10개를 반환
    """
    kw = request.args.get("city", "").strip()
    if not kw:
        return jsonify([]), 400

    pattern = f"%{kw}%"
    results = (
        Airport.query
        .filter(
            or_(
                Airport.city_en.ilike(pattern),
                Airport.name_en.ilike(pattern),
                Airport.name_ko.ilike(pattern)
            )
        )
        .order_by(Airport.city_en)  # 원한다면 정렬 기준 조정
        .limit(10)
        .all()
    )

    return jsonify([
        {
            "code": a.iata_code,
            "name": a.name_en,
            "city": a.city_en
        }
        for a in results
    ]), 200



with app.app_context():
        db.create_all()

if __name__ == "__main__":
    # 앱 컨텍스트에서 테이블 생성
    app.run(debug=True)