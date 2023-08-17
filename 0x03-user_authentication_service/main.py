#!/usr/bin/env python3
"""
Main file
"""
from auth import Auth
import requests

URL = 'http://127.0.0.1:5000/{}'


def register_user(email: str, password: str) -> None:
    """
    Test user registration
    """
    payload = {'email': email, 'password': password}
    resp = requests.post(URL.format('users'), data=payload)

    assert resp.json() == {'email': email, 'message': 'user created'}
    assert resp.status_code == 200


def log_in_wrong_password(email: str, password: str) -> None:
    """Test wrong password login"""
    payload = {'email': email, 'password': password}
    resp = requests.post(URL.format('sessions'), data=payload)

    assert resp.status_code == 401


def log_in(email: str, password: str) -> str:
    """Test successful login"""
    payload = {'email': email, 'password': password}
    resp = requests.post(URL.format('sessions'), data=payload)

    assert resp.status_code == 200
    assert resp.json() == {'email': email, 'message': 'logged in'}

    return resp.cookies.get('session_id')


def profile_unlogged() -> None:
    """
    Test user's profile is inactive
    """
    resp = requests.get(URL.format('profile'))
    assert resp.status_code == 403


def profile_logged(session_id: str) -> None:
    """
    Test user's profile is active
    """
    resp = requests.get(URL.format('profile'), cookies=session_id)
    # get user's email
    assert resp.status_code == 200


def log_out(session_id: str) -> None:
    """
    Test profile logout
    """
    resp = requests.delete(URL.format('sessions'), cookies=session_id)
    assert resp.url == URL.format('')


def reset_password_token(email: str) -> str:
    """
    test POST /reset_password route
    """
    payload = {'email': email}
    resp = requests.post(URL.format('reset_password'), data=payload)

    reset_token = resp.json()['reset_token']
    assert resp.status_code == 200
    assert resp.json() == {'email': email, 'reset_token': reset_token}

    return reset_token


def update_password(email: str, reset_token: str, new_password: str) -> None:
    """
    test PUT /reset_password route
    """
    payload = {
        'email': email,
        'reset_token': reset_token,
        'new_password': new_password
    }
    resp = requests.put(URL.format('reset_password'), data=payload)
    assert resp.json() == {"email": email, "message": "password updated"}
    assert resp.status_code == 200


EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"

if __name__ == '__main__':
    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    profile_logged(session_id)
    log_out(session_id)
    reset_token = reset_password_token(EMAIL)
    update_password(EMAIL, reset_token, NEW_PASSWD)
    log_in(EMAIL, NEW_PASSWD)
