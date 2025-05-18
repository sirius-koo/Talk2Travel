import os 


class Config:
    DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")