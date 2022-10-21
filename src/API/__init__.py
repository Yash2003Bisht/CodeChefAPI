from flask import Flask
app = Flask(__name__)

def index():
    from .endpoints import endpoints
    app.register_blueprint(endpoints, url_prefix="/")
    return app
