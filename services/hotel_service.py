from amadeus import Client, ResponseError
from config import Config

# ── Amadeus Client 인스턴스 ─────────────────────────────────
amadeus = Client(
    client_id=Config.AMADEUS_CLIENT_ID,
    client_secret=Config.AMADEUS_CLIENT_SECRET
)

def airport_to_city_code_via_api(airport_code: str) -> str:
    """
    Amadeus Reference API를 통해 공항 IATA 코드(ex: 'ITM')에 대응하는
    도시 IATA 코드(ex: 'OSA')를 조회합니다. (파라미터는 리스트 형태로 넘겨야 함)
    """
    try:
        resp = amadeus.reference_data.locations.airports.get(
            airportCodes=[airport_code]
        )
        data = resp.data or []
        if not data:
            return None
        return data[0].get("address", {}).get("cityCode")
    except ResponseError as err:
        print(f"[HotelService:airport_to_city_code_via_api] Amadeus API Error: {err}")
        return None

def get_hotel_ids_from_airport(airport_code: str, max_results: int = 10) -> list:
    """
    (1) airport_code(ex: 'ITM') → airport_to_city_code_via_api → city_code('OSA')
    (2) 변환된 city_code를 이용해 hotels/by-city 호출 → hotelId 리스트 반환
    """
    city_code = airport_to_city_code_via_api(airport_code)
    if not city_code:
        return []

    try:
        resp = amadeus.reference_data.locations.hotels.by_city.get(cityCode=city_code)
        data = resp.data or []
        return [item.get("hotelId") for item in data if item.get("hotelId")][:max_results]
    except ResponseError as err:
        print(f"[HotelService:get_hotel_ids_from_city] Amadeus API Error: {err}")
        return []

def search_hotels(
    hotel_ids: str,
    check_in_date: str,
    check_out_date: str,
    adults: int,
    room_quantity: int,
    max_results: int = 20
) -> list:
    """
    hotelIds (쉼표로 연결된 문자열)와 체크인/체크아웃 날짜, 인원수 등을 전달해
    '/v2/shopping/hotel-offers' 호출 → 호텔 오퍼 리스트 반환
    """
    try:
        resp = amadeus.shopping.hotel_offers_search.get(
            hotelIds=hotel_ids,
            checkInDate=check_in_date,
            checkOutDate=check_out_date,
            adults=adults,
            roomQuantity=room_quantity,
            page={"limit": max_results}
        )
        return resp.data or []
    except ResponseError as err:
        print(f"[HotelService:search_hotels] Amadeus API Error: {err}")
        return []