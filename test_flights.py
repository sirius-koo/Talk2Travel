from services.flight_service import search_flights

if __name__ == "__main__":
    offers = search_flights(
        city_from="ICN",
        city_to="TYO",
        start_date="2025-06-01",
        end_date="2025-06-05",
        adults=1,
        max_results=5
    )
    print("Offers:", offers)
