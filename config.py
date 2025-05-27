import os
from dotenv import load_dotenv

# .env 파일 읽어 환경변수로 설정
load_dotenv()

class Config:
    AMADEUS_CLIENT_ID     = os.getenv("AMADEUS_CLIENT_ID")
    AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
    RAPIDAPI_KEY          = os.getenv("RAPIDAPI_KEY")
    RAPIDAPI_HOST         = os.getenv("RAPIDAPI_HOST")