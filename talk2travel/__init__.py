from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config") # 임시

    @app.route("/")
    def index():
        return "Talk2Travel API is alive!"
    
    return app