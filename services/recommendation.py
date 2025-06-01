def rank_flights_by_price(offers: list, top_n: int = 3) -> list:
    """
    FlightOffers 리스트를 price.total 기준으로 오름차순 정렬해 상위 top_n 건 반환
    """
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
    flight-offer 객체에서 사용자에게 보여줄 최소 정보만 추출 (한국어 키)
    - 연결편이 있는 경우도 고려해, 첫 세그먼트의 출발지와 마지막 세그먼트의 도착지를 모두 표시
    """
    # offer["itineraries"][0]["segments"] 는 segments 리스트를 반환합니다.
    segs = offer["itineraries"][0]["segments"]
    first_seg = segs[0]
    last_seg  = segs[-1]

    # 가격 및 통화
    price_total = offer.get("price", {}).get("total")
    currency    = offer.get("price", {}).get("currency")
    price_str   = f"{price_total} {currency}" if price_total and currency else None

    return {
        "항공사":     first_seg["carrierCode"],
        "편명":       first_seg["number"],
        "출발공항":   first_seg["departure"]["iataCode"],
        "출발시각":   first_seg["departure"]["at"],
        "도착공항":   last_seg["arrival"]["iataCode"],
        "도착시각":   last_seg["arrival"]["at"],
        "가격":       price_str
    }


def simplify_hotel(offer: dict) -> dict:
    """
    hotel-offers 객체에서 사용자에게 보여줄 최소 정보만 추출 (한국어 키)
    """
    hot         = offer["hotel"]
    room_offer  = offer["offers"][0]

    # 설명 텍스트
    desc = room_offer.get("room", {}) \
                     .get("description", {}) \
                     .get("text")
    if not desc:
        desc = room_offer.get("roomInformation", {}) \
                         .get("description", "")

    price_total    = room_offer["price"]["total"]
    price_currency = room_offer["price"]["currency"]
    price_str      = f"{price_total} {price_currency}"

    return {
        "숙소명":   hot.get("name"),
        "체크인":   room_offer.get("checkInDate"),
        "체크아웃": room_offer.get("checkOutDate"),
        "세부사항": desc,
        "가격":     price_str
    }