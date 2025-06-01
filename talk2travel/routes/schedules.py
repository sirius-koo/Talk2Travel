# E:\Capstone1\Talk2Travel\talk2travel\routes\schedules.py

from flask import Blueprint, request, jsonify
from ..models import db, Schedule
from datetime import datetime
from flask_login import current_user

from services.flight_service import search_flights
from services.hotel_service import get_hotel_ids_from_airport, search_hotels
from services.recommendation import (
    rank_flights_by_price, simplify_flight,
    rank_hotels_by_price,  simplify_hotel
)

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
        "id":         sched.id,
        "title":      sched.title,
        "city":       sched.city,
        "start":      iso_date(sched.start),
        "end":        iso_date(sched.end),
        "passengers": sched.passengers,
        "budget":     sched.budget
    }), 201

@bp.get('/')
def list_schedules():
    rows = Schedule.query.filter_by(user_id=current_user.id).all()
    return jsonify([
        {
            "id":    s.id,
            "title": s.title,
            "start": iso_date(s.start),
            "end":   iso_date(s.end)
        }
        for s in rows
    ])

@bp.post('/recommendations')
def get_recommendations():
    data        = request.get_json()
    origin      = data['origin']       # ex: "ICN"
    destination = data['destination']  # ex: "ITM"
    start_date  = data['start_date']   # ex: "2025-07-03"
    end_date    = data['end_date']     # ex: "2025-07-07"
    passenger   = data.get('passenger', 1)
    budget      = data.get('budget', None)

    # ── 1) 항공편 검색 → 가격순 상위 3건 → 최소 정보 변환 ─────────
    raw_flights = search_flights(
        city_from=origin,
        city_to=destination,
        start_date=start_date,
        end_date=end_date,
        adults=passenger,
        max_results=20
    ) or []
    ranked_flights = rank_flights_by_price(raw_flights, top_n=3)
    top_flights    = [simplify_flight(offer) for offer in ranked_flights]

    # ── 2) 호텔 검색: airportCode → cityCode via API → Hotel IDs → Offers ───
    hotel_ids_list = get_hotel_ids_from_airport(destination, max_results=10)
    if not hotel_ids_list:
        top_hotels = []
    else:
        raw_hotels = search_hotels(
            hotel_ids=",".join(hotel_ids_list),
            check_in_date=start_date,
            check_out_date=end_date,
            adults=passenger,
            room_quantity=1,
            max_results=20
        ) or []
        ranked_hotels = rank_hotels_by_price(raw_hotels, top_n=3)
        top_hotels    = [simplify_hotel(h) for h in ranked_hotels]

    return jsonify({
        'flights': top_flights,
        'hotels':  top_hotels
    })

@bp.get('/test')
def test_ping():
    return 'schedules blueprint OK', 200
