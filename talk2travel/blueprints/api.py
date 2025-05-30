from flask import Blueprint, request, jsonify
from ..models import db, Schedule
from datetime import datetime
from flask_login import current_user
from services.recommendation import simplify_flight, simplify_hotel

api_bp = Blueprint('api', __name__, url_prefix='/api')

def iso_date(d):
    return d.isoformat() if d else None

@api_bp.post('/')
def create_schedule():
    data = request.get_json()
    sched = Schedule(
        user_id=current_user.id,
        title=f"{data['city']} Trip",
        city=data['city'],
        start=datetime.fromisoformat(data['start']).date(),
        end=datetime.fromisoformat(data['end']).date(),
        passengers=data.get('passengers', 1),
        budget=data.get('budget', 0)
    )
    db.session.add(sched)
    db.session.commit()
    return jsonify({
        "id": sched.id,
        "title": sched.title,
        "city": sched.city,
        "start": iso_date(sched.start),
        "end": iso_date(sched.end),
        "passengers": sched.passengers,
        "budget": sched.budget
    }), 201

@api_bp.get('/')
def list_schedules():
    rows = Schedule.query.filter_by(user_id=current_user.id).all()
    return jsonify([{ "id": s.id, "title": s.title, "start": iso_date(s.start), "end": iso_date(s.end) } for s in rows])

@api_bp.route('/recommendations', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    origin      = data['origin']       # 예: ICN
    destination = data['destination']  # 예: KIX
    start_date  = data['start_date']   # 예: '2025-07-03'
    end_date    = data['end_date']     # 예: '2025-07-07'
    passenger   = data.get('passenger', 1)
    budget      = data.get('budget', None)

    # 항공 Top3
    flights = simplify_flight(origin, destination, start_date, end_date)
    top_flights = flights[:3]

    # 숙소 Top3
    hotels = simplify_hotel(destination, start_date, end_date)
    top_hotels = hotels[:3]

    return jsonify({
        'flights': top_flights,
        'hotels':  top_hotels
    })