from flask import Blueprint, request, jsonify
from ..models import db, Schedule
from datetime import datetime
from flask_login import current_user

bp = Blueprint('schedules', __name__, url_prefix='/api/schedules')

def iso_date(d):
    return d.isoformat() if d else None

@bp.post('/')
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

@bp.get('/')
def list_schedules():
    rows = Schedule.query.filter_by(user_id=current_user.id).all()
    return jsonify([{ "id": s.id, "title": s.title, "start": iso_date(s.start), "end": iso_date(s.end) } for s in rows])