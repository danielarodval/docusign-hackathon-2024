import os
from flask import Flask, jsonify, redirect, send_from_directory, session, url_for
from __init__ import create_app
from auth_code_grant import docusign_auth_grant

app = create_app()


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react_app(path):
    print(f"Entering serve_react_app, path: {path}")
    
    # Check if user is authenticated
    if "docusign_token" not in session:
        print("No token in session, redirecting to auth")
        return redirect("/auth/")
    # Check if in development mode
    if app.config["VITE_MODE"] == "development":
        print("Dev mode, redirecting to React dev server")
        return redirect("http://localhost:3000/")
    
    # Serve static files from the frontend directory
    full_path = os.path.join(app.static_folder, path)
    print(f"Prod mode, full path: {full_path}")
    if path != "" and os.path.exists(full_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

@app.route("/check_access_token", methods=['GET'])
def check_login():
    check_auth();
    documents = {"message": "access token exist!"} 
    return jsonify(documents)

def check_auth():
    if("docusign_token" not in session):
        return redirect(url_for("auth_code_grant.login"))
    else:
        return None;
    
if __name__ == "__main__":
    app.run(debug=True)
