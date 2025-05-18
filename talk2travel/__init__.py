from flask import Flask
from .blueprints.api import api_bp
from .blueprints.core import core_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config") # 임시
    
    # API BluePrint
    app.register_blueprint(api_bp)

    # Core(UI) BluePrint
    app.register_blueprint(core_bp)
    
    return app