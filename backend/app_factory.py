import os
from flask import Flask
from redis import Redis
from requests import Session
from backend.ds_config import DS_CONFIG
from backend.services.agreements import agreements_bp
from backend.authentication.auth_code_grant import docusign_auth_grant
from backend.authentication.token_management import token_management_bp
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS

from dotenv import load_dotenv
def create_app():
    app = Flask(
        __name__,
        static_folder="../frontend/dist",  # Corrected path
        template_folder="../frontend/dist",  # Corrected path
        static_url_path=""  # This ensures URLs for static files don't include "static"
    )
    # see https://flask-wtf.readthedocs.io/en/stable/csrf.html
    csrf = CSRFProtect(app)

    # Enable CORS
    CORS(app, supports_credentials=True)
    

    # app.config['SESSION_TYPE'] = 'redis'
    # app.config['SESSION_REDIS'] = Redis.from_url("redis://127.0.0.1:6379")
    # Session(app)
    dotenv_path = os.path.join("../env", ".env")
    load_dotenv(override=True)
    app.config['FLASK_ENV'] = os.getenv('FLASK_ENV')
    app.config['VITE_MODE'] = os.getenv('VITE_MODE')
    print("What type is app.config from 'VITE_MODE'", app.config['VITE_MODE'])
    app.secret_key = DS_CONFIG["ds_client_secret"]
    app.register_blueprint(docusign_auth_grant)
    app.register_blueprint(token_management_bp)
    app.register_blueprint(agreements_bp)
    
    return app
