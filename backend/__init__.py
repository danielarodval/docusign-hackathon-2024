import os
from flask import Flask
from auth_code_grant import docusign_auth_grant
from ds_config import DS_CONFIG
from dotenv import load_dotenv

def create_app():
    print("init.py")
    app = Flask(
        __name__,
        static_folder="D:/HACKATHON/RentalAgreement-python/frontend/dist",  # Corrected path
        template_folder="D:/HACKATHON/RentalAgreement-python/frontend/dist",  # Corrected path
        static_url_path=""  # This ensures URLs for static files don't include "static"
    )
    dotenv_path = os.path.join("env", ".env")
    load_dotenv(override=True)
    app.config['FLASK_ENV'] = os.getenv('FLASK_ENV')
    app.config['VITE_MODE'] = os.getenv('VITE_MODE')
    print("What type is app.config from 'VITE_MODE'", app.config['VITE_MODE'])
    app.secret_key = DS_CONFIG["ds_client_secret"]
    app.register_blueprint(docusign_auth_grant, url_prefix="/auth")
    return app

