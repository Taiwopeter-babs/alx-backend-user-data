#!/usr/bin/env python3
"""
Route module for the API
"""
from os import getenv
from api.v1.views import app_views
from flask import Flask, jsonify, abort, request, Response
from flask_cors import (CORS, cross_origin)
import os
from typing import Tuple


app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})
auth = None or os.getenv('AUTH_TYPE')

# check for auth env variable
if auth is not None:
    from api.v1.auth.auth import Auth
    if auth == 'auth':
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
            a `401 Unauthorized` error is returned.
        - if the `Authorization` header string is not valid,
            a `403 Forbidden` error is returned.
    """
    excluded_paths = [
        '/api/v1/status/',
        '/api/v1/unauthorized/',
        '/api/v1/forbidden/'
    ]

    if auth:
        # check if the request path requires authentication
        if auth.require_auth(request.path, excluded_paths):
            # check if the `Authorization` header has a value
            if auth.authorization_header(request) is None:
                abort(401)
            if auth.current_user(request) is None:
                abort(403)


@app.errorhandler(404)
def not_found(error) -> Tuple[Response, int]:
    """ Not found handler
    """
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(401)
def unauthorized(error) -> Tuple[Response, int]:
    """ Unauthorized handler
    """
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden(error) -> Tuple[Response, int]:
    """ Forbidden handler
    """
    return jsonify({"error": "Forbidden"}), 403


if __name__ == "__main__":
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    app.run(host=host, port=port)
