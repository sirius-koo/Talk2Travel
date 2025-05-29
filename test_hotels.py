# E:\Capstone1\Talk2Travel\test_hotels.py

import json
from services.hotel_service import get_hotel_ids, search_hotels

if __name__ == "__main__":
    # 1) 도심 코드로 hotelId 리스트 먼저 가져오기
    city_code = "PAR"  # 예: 파리
    ids = get_hotel_ids(city_code, max_results=5)
    print("Hotel IDs:", ids)
    if not ids:
        print("호텔 ID를 찾을 수 없습니다. city_code를 확인하세요.")
        exit(1)

    # 2) 쉼표로 연결된 hotelIds 문자열 생성
    hotel_ids_param = ",".join(ids)

    # 3) 호텔 오퍼 검색
    offers = search_hotels(
        hotel_ids=hotel_ids_param,
        check_in_date="2025-06-01",
        check_out_date="2025-06-05",
        adults=2,
        room_quantity=1,
        max_results=5
    )

    # 4) 결과 출력
    print("Hotel Offers:")
    if not offers:
        print("  (No offers returned or API error)")
    else:
        print(json.dumps(offers, indent=2, ensure_ascii=False))
