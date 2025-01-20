import os
from flask import Flask, Blueprint, jsonify,redirect, render_template, send_from_directory, url_for, session, request
from flask_oauthlib.client import OAuth
from docusign_esign import ApiClient
from docusign_esign.apis.authentication_api import AuthenticationApi
import requests
from ds_config import DS_CONFIG


docusign_auth_grant = Blueprint('auth_code_grant', __name__)
docusign_auth_grant.secret_key = DS_CONFIG["ds_client_secret"]

api_client = ApiClient();
oauth = OAuth(docusign_auth_grant)
request_token_params = {
    "scope":"adm_store_unified_repo_read"
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



@docusign_auth_grant.route("/")
def index():
    if "docusign_token" not in session:
        return redirect(url_for('auth_code_grant.login'))
    return redirect(url_for("serve_react_app", path=""))

@docusign_auth_grant.route("/login")
def login():
    return docusign.authorize(callback=url_for("auth_code_grant.callbackFunc",_external=True))

@docusign_auth_grant.route("/callback")
def callbackFunc():
    response = docusign.authorized_response()
    if response is None or response.get("access_token") is None:
        return "Access denied: reason={} error={}".format(
            request.args.get("error", "Unknown"),
            request.args.get("error_description", "No description")
        )
    session["docusign_token"] = (response["access_token"], "")
    return redirect(url_for("serve_react_app", path=""))


# @docusign.tokengetter 
# def get_docusign_oauth_token(): 
#     return session.get("docusign_token")


