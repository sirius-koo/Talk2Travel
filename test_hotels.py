from services.hotel_service import search_hotels

if __name__ == "__main__":
    offers = search_hotels(
        dest_id="-2092174",
        arrival_date="2025-06-01",
        departure_date="2025-06-05",
        adults=2,
        currency="KRW",
        locale="en-gb",
        max_results=5
    )
    print("Hotel Offers:", offers)
