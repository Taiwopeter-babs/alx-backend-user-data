#!/usr/bin/env python3
""" Module of Session views
"""
from api.v1.views import app_views
from flask import jsonify, abort, request, make_response
from models.user import User
import os


@app_views.route('/auth_session/login', methods=['POST'], strict_slashes=False)
def session_login() -> str:
    """ POST /api/v1/auth_session/login
    """
    email = request.form.get('email')
    password = request.form.get('password')

    if email is None or len(email) == 0:
        return jsonify({"error": "email missing"}), 400
    if password is None or len(password) == 0:
        return jsonify({"error": "password missing"}), 400

    user = User.search({"email": email})
    # no user found
    if len(user) == 0:
        return jsonify({"error": "no user found for this email"}), 404
    user_obj = user[0]
    # check password
    if not user_obj.is_valid_password(password):
        return jsonify({"error": "wrong password"}), 401

    # create session id
    from api.v1.app import auth
    user_sess_id = auth.create_session(user_obj.id)

    # set response and cookie
    cookie_name, cookie_value = os.getenv('SESSION_NAME'), user_sess_id
    resp = make_response(jsonify(user_obj.to_json()))
    resp.set_cookie(cookie_name, cookie_value)

    return resp


@app_views.route('/auth_session/logout', methods=['DELETE'],
                 strict_slashes=False)
def session_logout() -> str:
    """ `DELETE /api/v1/auth_session/logout`
    - Logs out a user from the current session
    """
    from api.v1.app import auth
    # delete session id
    if not auth.destroy_session(request):
        abort(404)
    return jsonify({}), 200
