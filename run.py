import base64
import os
import sys
from dotenv import load_dotenv
from flask import Flask, json, jsonify, redirect, send_from_directory, session, url_for
import requests

from backend.app_factory import create_app
from backend.authentication.auth_code_grant import get_user_info

app = create_app()


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react_app(path):
    dotenv_path = os.path.join("../env", ".env")
    load_dotenv(dotenv_path)
    dev_server_url = os.getenv("REACT_DEV_URL")
    
    #if "docusign_token" in session:
    #   remove_session_element("docusign_token")

    # Check if user is authenticated
    if "docusign_token" not in session:
        print("No token in session, redirecting to auth")
        return redirect(url_for("auth_code_grant.index"))
    # Check if in development mode
    if "userInfo" not in session and "docusign_token" in session:
        print("No userInfo so must call it!")
        get_user_info()

    print("UserInfo from session:",session.get("userInfo"))
    print("Docusign token: ", session.get("docusign_token"))
    userinfo = session.get("userInfo")

    if userinfo is not None and "error" in userinfo:
        session.pop("userInfo")
        session.pop("docusign_token")
        redirect(url_for("auth_code_grant.index"))
    else:
        redirect(url_for("auth_code_grant.index"))

    if app.config["VITE_MODE"] == "development":
        print("Dev mode, redirecting to React dev server")
        return redirect(dev_server_url)
    
    # Serve static files from the frontend directory
    full_path = os.path.join(app.static_folder, path)
    print(f"Prod mode, full path: {full_path}")
    if path != "" and os.path.exists(full_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

def remove_session_element(key):
    """
    Remove a specific element from the session.
    
    :param key: The key of the element to remove from the session
    :return: True if the element was removed, False if it didn't exist
    """
    if key in session:
        session.pop(key, None)
        return True
    return False
if __name__ == "__main__":
    app.run(debug=True)
