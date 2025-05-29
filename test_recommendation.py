import json
from services.flight_service import search_flights
from services.hotel_service import get_hotel_ids, search_hotels
from services.recommendation import (
    rank_flights_by_price,
    rank_hotels_by_price,
    simplify_flight,
    simplify_hotel
)
city_from = "ICN"; city_to = "PAR"
start_date = "2025-06-01"; end_date="2025-06-05"

if __name__ == "__main__":
    # Flight 추천
    flight_offers = search_flights(
        city_from=city_from,
        city_to=city_to,
        start_date=start_date,
        end_date=end_date,
        adults=1,
        max_results=10
    )
    top_flights = rank_flights_by_price(flight_offers, top_n=3)
    simple_flights = [simplify_flight(o) for o in top_flights]
    print("Top 3 Flights:")
    print(json.dumps(simple_flights, indent=2, ensure_ascii=False))

    # Hotel 추천
    ids = get_hotel_ids(city_to, max_results=5)
    hotel_ids_param = ",".join(ids)
    hotel_offers = search_hotels(
        hotel_ids=hotel_ids_param,
        check_in_date=start_date,
        check_out_date=end_date,
        adults=2,
        room_quantity=1,
        max_results=10
    )
    top_hotels = rank_hotels_by_price(hotel_offers, top_n=3)
    simple_hotels = [simplify_hotel(o) for o in top_hotels]
    print("\nTop 3 Hotels:")
    print(json.dumps(simple_hotels, indent=2, ensure_ascii=False))