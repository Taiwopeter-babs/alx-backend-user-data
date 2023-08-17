#!/usr/bin/env python3
"""
Application module
"""
from auth import Auth
from flask import (
    abort,
    Flask,
    jsonify,
    request, redirect, make_response,
    url_for
)

app = Flask(__name__)
app.url_map.strict_slashes = False

# instantiate the Auth
AUTH = Auth()


@app.route('/', methods=['GET'])
def get_message() -> str:
    """A simple GET / route"""
    return jsonify({"message": "Bienvenue"})


@app.route('/users', methods=['POST'])
def users() -> str:
    """
    POST /users
    - Registers a new user
    """
    email = request.form.get('email')
    password = request.form.get('password')

    # check for existing user
    try:
        user = AUTH.register_user(email, password)
    except ValueError:
        return jsonify({"message": "email already registered"}), 400

    return jsonify({
        "email": user.email,
        "message": "user created"
    })


@app.route('/sessions/', methods=['POST'])
def login() -> str:
    """
    POST /sessions
    - login to a session
    """
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        abort(401)

    # check for valid user
    if not AUTH.valid_login(email, password):
        abort(401)

    # set response and cookie
    cookie_name, cookie_value = 'session_id', AUTH.create_session(email)
    if cookie_value is None:
        abort(401)

    json_msg = {"email": "{}".format(email), "message": "logged in"}
    resp = make_response(jsonify(json_msg))
    resp.set_cookie(cookie_name, cookie_value)

    return resp


@app.route('/sessions/', methods=['DELETE'])
def logout() -> str:
    """
      DELETE /sessions
    - logout from a session
    """
    # get `session_id` cookie
    session_id = request.cookies.get('session_id')

    # get user by session id
    user = AUTH.get_user_from_session_id(session_id)
    if user is None:
        abort(403)
    # remove user's session id from storage
    AUTH.destroy_session(user.id)

    # redirect to home '/'
    return redirect(url_for('app.get_message'))


@app.route('/profile', methods=['GET'])
def profile() -> str:
    """
    GET /profile
    - returns a user info
    """
    # get `session_id` cookie
    session_id = request.cookies.get('session_id')

    # get user by session id
    user = AUTH.get_user_from_session_id(session_id)
    if user is None:
        abort(403)

    return jsonify({'email': user.email}), 200


@app.route('/reset_password', methods=['POST'])
def get_reset_password_token() -> str:
    """
    POST /reset_password
    - resets a user password
    """
    email = request.form.get('email')
    if email is None:
        abort(401)

    try:
        reset_token = AUTH.get_reset_password_token(email)
    except ValueError:
        abort(403)

    return jsonify({"email": email, "reset_token": reset_token}), 200


@app.route('/reset_password', methods=['PUT'])
def update_password() -> str:
    """
    POST /reset_password
    - resets a user password
    """
    email = request.form.get('email')
    reset_token = request.form.get('reset_token')
    new_password = request.form.get('new_password')

    if email is None or reset_token is None \
            or new_password is None:
        abort(401)

    try:
        AUTH.update_password(reset_token, new_password)
    except ValueError:
        abort(403)

    return jsonify({"email": email, "message": "password updated"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
