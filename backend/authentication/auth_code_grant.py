import os
import time
from flask import Flask, Blueprint, jsonify,redirect, render_template, send_from_directory, url_for, session, request
from flask_oauthlib.client import OAuth
from docusign_esign import ApiClient
from docusign_esign.apis.authentication_api import AuthenticationApi
import requests
from backend.ds_config import DS_CONFIG


docusign_auth_grant = Blueprint('auth_code_grant', __name__, url_prefix="/auth_code_grant")
docusign_auth_grant.secret_key = DS_CONFIG["ds_client_secret"]

api_client = ApiClient();
oauth = OAuth(docusign_auth_grant)
# request_token_params = [
#     "signature ",
#     "adm_store_unified_repo_read",
#     "models_read"
# ]

request_token_params = {
    "scope": "signature adm_store_unified_repo_read cors"
}

docusign = oauth.remote_app(
        "docusign",
        consumer_key=DS_CONFIG["ds_client_id"],
        consumer_secret=DS_CONFIG["ds_client_secret"],
        access_token_url=DS_CONFIG["authorization_server"] + "/oauth/token",
        authorize_url=DS_CONFIG["authorization_server"] + "/oauth/auth",
        request_token_params=request_token_params,
        base_url=None,
        request_token_url=None,
        access_token_method="POST"
)


@docusign_auth_grant.route("/index")
def index():
    if ("docusign_token" not in session) or ("refresh_token" not in session) or ("expires_in" not in session):
        return redirect(url_for('auth_code_grant.login'))
    return redirect(url_for("serve_react_app", path="/"))

# @docusign_auth_grant.route("/login")
# def login():
#     return docusign.authorize(callback=url_for("auth_code_grant.callbackFunc",_external=True))

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5000",
    "https://account-d.docusign.com",
    "https://demo.docusign.net",
    "https://demo.docusign.net/restapi"
]

@docusign_auth_grant.route("/login", methods=['OPTIONS', 'GET'])
def login():
    if request.method == 'OPTIONS':
        if request.headers.get("Origin") in allowed_origins:
            response = jsonify({"message": "login OK"})
            response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin"))
            response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response
        else:
            return jsonify({"message": "Origin not allowed"}), 403
    elif request.method == 'GET':
        if request.headers.get("Origin") in allowed_origins:
            response = docusign.authorize(callback=url_for("auth_code_grant.callbackFunc",_external=True))
            response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin"))
            response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response
            #return docusign.authorize(callback=url_for("auth_code_grant.callbackFunc",_external=True))
        else:
            return jsonify({"message": "Origin not allowed"}), 403

# @app.route('/login', methods=['OPTIONS', 'GET'])
# def login():
#     if request.method == 'OPTIONS':
#         response = jsonify({"message": "preflight OK"})
#         response.headers.add("Access-Control-Allow-Origin", "*")
#         response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
#         response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
#         return response
#     else:
#         response = jsonify({"message": "login OK"})
#         response.headers.add("Access-Control-Allow-Origin", "*")
#         return response

@docusign_auth_grant.route("/callback")
def callbackFunc():
    response = docusign.authorized_response()
    if response is None or response.get("access_token") is None:
        return "Access denied: reason={} error={}".format(
            request.args.get("error", "Unknown"),
            request.args.get("error_description", "No description")
        )
    print("Response json of callBackFunc",response)
    session["docusign_token"] = response["access_token"]
    session["refresh_token"] = response["refresh_token"]
    buffer_time = 30*60
    adjusted_expiration = response['expires_in'] - buffer_time
    expiration_timestamp = int(time.time()) + adjusted_expiration # 7 hours and 30 minutes (27000 timestamp change)
    session["expires_in"] =  expiration_timestamp #stored as timestamp
    session["scope"] = response["scope"]
    print(session['expires_in'])
    return redirect(url_for("auth_code_grant.get_user_info"))

@docusign_auth_grant.route("/get_user_info")
def get_user_info():
    access_token = session.get("docusign_token")
    if not access_token or not isinstance(access_token, str) or len(access_token) < 1:
        return redirect(url_for("auth_code_grant.login"))
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        userinfo_response = requests.get(f"{DS_CONFIG['authorization_server']}/oauth/userinfo", headers=headers)
        userinfo_response.raise_for_status()  # Raises an HTTPError for bad responses
        user_info = userinfo_response.json()
        session['base_uri'] = user_info['accounts'][0]["base_uri"]
        session['account_id'] = user_info['accounts'][0]["account_id"]
        return redirect(url_for("serve_react_app", path="/"))
    except requests.exceptions.RequestException as e:
        print(f"Error fetching user info: {e}")
        return jsonify({"error": "Failed to fetch user info"}), 500