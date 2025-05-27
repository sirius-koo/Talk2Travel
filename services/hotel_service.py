import requests
from config import Config

def search_hotels(
    dest_id: str = "-2092174",
    arrival_date: str = "2025-06-01",
    departure_date: str = "2025-06-05",
    adults: int = 1,
    currency: str = "KRW",
    locale: str = "en-gb",
    max_results: int = 20
):
    """
    Booking.com RapidAPI 호텔 검색
    필수 파라미터:
      - dest_id:         도시 식별자 (예: "-2092174")
      - search_type:     CITY (고정)
      - arrival_date:    체크인 YYYY-MM-DD
      - departure_date:  체크아웃 YYYY-MM-DD
    옵션:
      - adults, currency, locale, page_size 등
    """
    url = "https://booking-com.p.rapidapi.com/v1/hotels/search"
    headers = {
        "X-RapidAPI-Key": Config.RAPIDAPI_KEY,
        "X-RapidAPI-Host": Config.RAPIDAPI_HOST
    }
    params = {
        "dest_id":        dest_id,
        "search_type":    "CITY",
        "arrival_date":   arrival_date,
        "departure_date": departure_date,
        "adults_number":  adults,
        "filter_by_currency": currency,
        "locale":         locale,
        "page_size":      max_results,
        # 필요하면 아래 옵션도 추가 가능
        # "order_by":       "popularity",
        # "units":          "metric",
    }

    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        print(f"[HotelService] Error {resp.status_code}: {resp.text}")
        return None

    data = resp.json()
    # JSON 구조에 따라 키가 다를 수 있습니다.
    # 예를 들어: data["result"], data["hotels"], data["data"] 등
    # 여기서는 전체 응답을 그대로 반환합니다.
    return data
