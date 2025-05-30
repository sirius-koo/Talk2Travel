# E:\Capstone1\Talk2Travel\scripts\seed_airports.py

import os
import sys
import csv

# 1) 이 스크립트 파일 위치에서 한 단계 위 폴더를 프로젝트 루트로 간주
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# 2) sys.path 가장 앞에 넣어, venv의 app 패키지가 아닌 이 프로젝트의 app.py를 찾게 함
sys.path.insert(0, PROJECT_ROOT)

# 이제 프로젝트 루트의 app.py 에서 가져옴
from app import app, db, Airport

CSV_PATH = os.path.join(PROJECT_ROOT, "data", "global_airport_IATA_info.csv")

def seed_airports():
    count = 0
    with open(CSV_PATH, encoding="cp949", newline="") as f:
        reader = csv.DictReader(f, fieldnames=[
            "name_en", "name_ko", "iata_code", "icao_code",
            "region", "country_en", "country_ko", "city_en"
        ])
        next(reader)  # 헤더 행 건너뛰기
        for row in reader:
            code = row["iata_code"].strip()
            if not code:
                continue
            airport = Airport(
                iata_code   = code,
                icao_code   = row["icao_code"] or None,
                name_en     = row["name_en"],
                name_ko     = row["name_ko"],
                region      = row["region"],
                country_en  = row["country_en"],
                country_ko  = row["country_ko"],
                city_en     = row["city_en"]
            )
            db.session.merge(airport)
            count += 1
    db.session.commit()
    print(f"✅ {count} airports seeded from {CSV_PATH}")

if __name__ == "__main__":
    # Flask 앱 컨텍스트 안에서 실행
    with app.app_context():
        seed_airports()
