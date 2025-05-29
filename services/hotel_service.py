from amadeus import Client, ResponseError
from config import Config

# Amadeus 클라이언트 초기화
amadeus = Client(
    client_id=Config.AMADEUS_CLIENT_ID,
    client_secret=Config.AMADEUS_CLIENT_SECRET
)

def get_hotel_ids(city_code: str, max_results: int = 10) -> list:
    """
    Amadeus Reference Data: Hotels by City 호출
    :param city_code: IATA 또는 UN/LOCODE (e.g. 'PAR' for Paris)
    :param max_results: 최대 ID 개수
    :return: hotelId 문자열 리스트
    """
    try:
        resp = amadeus.reference_data.locations.hotels.by_city.get(
            cityCode=city_code
        )
        data = resp.data  # dict 리스트
        # 앞에서 max_results개만 뽑아서 hotelId 리스트로 변환
        return [h["hotelId"] for h in data[:max_results]]
    except ResponseError as err:
        print(f"[HotelService] Error fetching hotel IDs: {err}")
        return []

def search_hotels(
    hotel_ids: str,
    check_in_date: str,
    check_out_date: str,
    adults: int = 1,
    room_quantity: int = 1,
    max_results: int = 20
) -> list:
    """
    Amadeus Hotel Offers Search API(v3) 호출
    :param hotel_ids: 쉼표로 구분된 hotelId 문자열
    :param check_in_date: 체크인(YYYY-MM-DD)
    :param check_out_date: 체크아웃(YYYY-MM-DD)
    """
    try:
        resp = amadeus.shopping.hotel_offers_search.get(
            hotelIds=hotel_ids,
            checkInDate=check_in_date,
            checkOutDate=check_out_date,
            adults=adults,
            roomQuantity=room_quantity,
            pageLimit=max_results
        )
        return resp.data  # 오퍼 리스트
    except ResponseError as err:
        print(f"[HotelService] Amadeus API Error: {err}")
        return []