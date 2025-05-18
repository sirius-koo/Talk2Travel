import os

class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")