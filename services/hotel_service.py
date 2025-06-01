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
    도시 IATA 코드(ex: 'OSA')를 조회합니다.
    성공 시 문자열 반환, 실패 시 None 반환.
    """
    try:
        # 파라미터 이름을 'airportCodes'로 수정
        resp = amadeus.reference_data.locations.airports.get(airportCodes=airport_code)
        data = resp.data or []
        if not data:
            return None

        # 첫 번째 결과의 address.cityCode 값을 도시 IATA 코드로 반환
        return data[0].get("address", {}).get("cityCode")
    except ResponseError as err:
        print(f"[HotelService:airport_to_city_code_via_api] Amadeus API Error: {err}")
        return None


def get_hotel_ids_from_airport(airport_code: str, max_results: int = 10) -> list:
    """
    (1) airport_code(ex: 'ITM')를 airport_to_city_code_via_api로 도시 IATA 코드(ex: 'OSA')로 변환
    (2) 변환된 city_code로 '/v1/reference-data/locations/hotels/by-city?cityCode={city_code}' 호출하여
        호텔 ID 목록을 반환 (최대 max_results개)
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
    hotelIds(쉼표로 연결된 문자열)와 체크인/체크아웃 날짜, 인원수 등을 전달해
    '/v2/shopping/hotel-offers'를 호출하여 호텔 오퍼 리스트를 반환합니다.
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