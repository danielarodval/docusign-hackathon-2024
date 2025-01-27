import os
from flask import Flask
from .authentication.auth_code_grant import docusign_auth_grant
from .authentication.token_management import token_management_bp
from .ds_config import DS_CONFIG
from dotenv import load_dotenv
from .services.agreements import agreements_bp


