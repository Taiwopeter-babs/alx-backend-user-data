#!/usr/bin/env python3
"""
Route module for the API
"""
from os import getenv
from api.v1.views import app_views
from flask import Flask, jsonify, abort, request
from flask_cors import (CORS, cross_origin)
import os
from typing import Tuple


app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})
auth = None or os.getenv('AUTH_TYPE')

# check for auth env variable
if auth is not None:
    if auth == 'session_auth':
        from api.v1.auth.session_auth import SessionAuth
        auth = SessionAuth()
    elif auth == 'auth':
        from api.v1.auth.auth import Auth
        auth = Auth()
    elif auth == 'basic_auth':
        from api.v1.auth.basic_auth import BasicAuth
        auth = BasicAuth()


@app.before_request
def check_auth_required() -> None:
    """
    check if the request path requires authentication.\n
    - if the request path requires auth;
        - if the `Authorization` header is not in request headers,
            and there's no session cookie, a `401 Unauthorized` error
            is returned.
        - if the `Authorization` header string is not valid,
            a `403 Forbidden` error is returned.
    """
    excluded_paths = [
        '/api/v1/stat*',
        '/api/v1/unauthorized/',
        '/api/v1/forbidden/',
        '/api/v1/auth_session/login/'
    ]

    if auth:
        # check if the request path requires authentication
        if auth.require_auth(request.path, excluded_paths):
            # check if the `Authorization` header has a value
            # and session cookie is present
            if auth.authorization_header(request) is None \
                    and auth.session_cookie(request) is None:
                abort(401)
            if auth.current_user(request) is None:
                abort(403)
            request.current_user = auth.current_user(request)


@app.errorhandler(404)
def not_found(error) -> Tuple[str, int]:
    """ Not found handler
    """
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(401)
def unauthorized(error) -> Tuple[str, int]:
    """ Unauthorized handler
    """
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden(error) -> Tuple[str, int]:
    """ Forbidden handler
    """
    return jsonify({"error": "Forbidden"}), 403


if __name__ == "__main__":
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    app.run(host=host, port=port)
