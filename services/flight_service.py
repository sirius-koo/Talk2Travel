from amadeus import Client, ResponseError
from config import Config

# Amadeus 클라이언트 초기화
amadeus = Client(
    client_id=Config.AMADEUS_CLIENT_ID,
    client_secret=Config.AMADEUS_CLIENT_SECRET
)

def search_flights(
    city_from: str,
    city_to: str,
    start_date: str,
    end_date: str,
    adults: int = 1,
    max_results: int = 10
):
    """
    Amadeus Flight Offers Search API 호출
    :param city_from: 출발 도시 코드 (예: ICN)
    :param city_to:   도착 도시 코드 (예: TYO)
    :param start_date: 출발일 (YYYY-MM-DD)
    :param end_date:   귀국일 (YYYY-MM-DD)
    :param adults:     탑승 인원 수
    :param max_results:최대 반환 개수
    :return: API가 반환한 오퍼 리스트 또는 None
    """
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=city_from,
            destinationLocationCode=city_to,
            departureDate=start_date,
            returnDate=end_date,
            adults=adults,
            max=max_results
        )
        return response.data
    except ResponseError as err:
        # 로깅 또는 예외 처리
        print(f"[FlightService] Amadeus API Error: {err}")
        return None