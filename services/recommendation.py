def rank_flights_by_price(offers: list, top_n: int = 3) -> list:
    """
    FlightOffers 리스트를 price.total 기준으로 오름차순 정렬해 상위 top_n 건 반환
    """
    # 가격 문자열을 float로 변환해 정렬
    sorted_offers = sorted(
        offers,
        key=lambda o: float(o.get("price", {}).get("total", float("inf")))
    )
    return sorted_offers[:top_n]


def rank_hotels_by_price(offers: list, top_n: int = 3) -> list:
    """
    HotelOffers 리스트를 offers[0].price.total 기준으로 오름차순 정렬해 상위 top_n 건 반환
    """
    def _extract_price(o):
        try:
            return float(o["offers"][0]["price"]["total"])
        except Exception:
            return float("inf")

    sorted_offers = sorted(offers, key=_extract_price)
    return sorted_offers[:top_n]


def simplify_flight(offer: dict) -> dict:
    """
    flight-offer 객체에서 사용자에게 보여줄 최소 정보만 추출
    """
    # 첫 번째 여정의 첫 번째 세그먼트
    seg = offer["itineraries"][0]["segments"][0]
    
    # 가격 및 통화
    price_total = offer.get("price", {}).get("total")
    currency    = offer.get("price", {}).get("currency")
    # "123.75 EUR" 형태로 변환
    price_str = f"{price_total} {currency}" if price_total and currency else None

    return {
        "airline":           seg["carrierCode"],           # 항공사 코드
        "flight_number":     seg["number"],                # 편명
        "departure_airport": seg["departure"]["iataCode"], # 출발 공항
        "departure_time":    seg["departure"]["at"],       # 출발 시각
        "arrival_airport":   seg["arrival"]["iataCode"],   # 도착 공항
        "arrival_time":      seg["arrival"]["at"],         # 도착 시각
        "price":             price_str                     # "총요금 통화"
    }


def simplify_hotel(offer: dict) -> dict:
    """
    hotel-offers 객체에서 사용자에게 보여줄 최소 정보만 추출
    """
    hot = offer["hotel"]
    room_offer = offer["offers"][0]

    # 설명 텍스트: room.description 안에 있는 text 사용
    # 또는 roomInformation.description (string) 중 하나 골라 사용
    description_data = room_offer.get("room", {}) \
                                .get("description", {}) \
                                .get("text")
    if not description_data:
        # roomInformation.description fallback
        description_data = room_offer.get("roomInformation", {}) \
                                     .get("description", "")

    # 가격 문자열: "<total> <currency>"
    price_total = room_offer["price"]["total"]
    price_currency = room_offer["price"]["currency"]
    price_str = f"{price_total} {price_currency}"

    return {
        "숙소명":    hot.get("name"),
        "체크인":    room_offer.get("checkInDate"),
        "체크아웃":  room_offer.get("checkOutDate"),
        "세부사항":  description_data,
        "가격":      price_str
    }