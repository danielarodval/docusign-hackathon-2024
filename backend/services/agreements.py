
from flask import Blueprint, json, jsonify, redirect, session, url_for
import requests

from backend.authentication.token_management import check_access_token

agreements_bp = Blueprint("agreements",__name__,url_prefix="/agreements")

dev_base_path = "https://api-d.docusign.com/v1"
@agreements_bp.route("/get_agreements",methods=["GET"])
def get_agreements():
    print("IN GET AGREEMENTS")
    check_auth()
    headers = {
        "Authorization": f"Bearer {session["docusign_token"]}",
        "Accept":"application/json",
        "Content-Type":"application/json"
    }
    base_uri = session.get("base_uri")
    account_id = session.get("account_id")
    print(account_id)
    try:
        agreements_response = requests.get(f"{dev_base_path}/accounts/{account_id}/agreements", headers=headers)
        agreements_response.raise_for_status()  # This will raise an exception for HTTP errors
        agreements_data = agreements_response.json()
    except requests.exceptions.RequestException as e:
            print(f"Error fetching user info: {e}")
            return jsonify({"error": "Failed to fetch user info"}), 500
    except json.JSONDecodeError:
            print("Failed to decode JSON response")
            return jsonify({"error": "Invalid response from DocuSign"}), 500
    print(agreements_data)
    return agreements_data


def check_auth():
    if("docusign_token" not in session):
        return redirect(url_for("auth_code_grant.login"))
    else:
        check_access_token()