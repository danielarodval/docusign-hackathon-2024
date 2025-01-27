import time
import base64
import requests
from flask import Blueprint, jsonify, redirect, session, url_for
from backend.ds_config import DS_CONFIG

token_management_bp = Blueprint("token_management", __name__, url_prefix="/token_management")

@token_management_bp.route("/")
def check_access_token():
    
    # if not all([access_token, refresh_token, expiration_time]):
    #     print("GO TO LOGIN")
    #     index()
    if ("docusign_token" not in session) or ("refresh_token" not in session) or ("expires_in" not in session):
        return redirect(url_for("auth_code_grant.index"))
    
    access_token = session.get("docusign_token") #needs to be a try catch
    refresh_token = session.get("refresh_token") #catch needs to call for new token
    expiration_time = session.get("expires_in")
    current_time = int(time.time())

    if current_time >= expiration_time:
        auth_string = f"{DS_CONFIG['ds_client_id']}:{DS_CONFIG['ds_client_secret']}"
        auth_header = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {auth_header}"
        }
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        try:# needs to be its own function
            response = requests.post(f"{DS_CONFIG['authorization_server']}/oauth/token", data=data, headers=headers)
            response.raise_for_status()
            new_token = response.json()
            
            buffer_time = 30 * 60  # 30 minutes in seconds
            adjusted_expiration = new_token['expires_in'] - buffer_time
            expiration_timestamp = int(time.time()) + adjusted_expiration
            
            session["docusign_token"] = new_token["access_token"]
            session["refresh_token"] = new_token["refresh_token"]
            session["expires_in"] = expiration_timestamp
            
            return jsonify({"message": "Token refreshed successfully"}), 200
        except requests.exceptions.RequestException as e:
            print(f"Error refreshing token: {e}")
            return jsonify({"error": "Failed to refresh token"}), 500
    else:
        return jsonify({"message": "Token is still valid"}), 200
