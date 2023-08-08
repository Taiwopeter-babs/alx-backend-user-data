#!/usr/bin/env python3
""" Main 100
"""
import base64
from api.v1.auth.basic_auth import BasicAuth
from models.user import User
import re
""" Create a user test """
# user_email = "bob100@hbtn.io"
# user_clear_pwd = "H0lberton:School:98!"

# user = User()
# user.email = user_email
# user.password = user_clear_pwd
# print("New user: {}".format(user.id))
# user.save()

# basic_clear = "{}:{}".format(user_email, user_clear_pwd)
# print("Basic Base64: {}".format(base64.b64encode(
#     basic_clear.encode('utf-8')).decode("utf-8")))
excluded_paths = ["/api/v1/stat*", '/api/v1/unauthorized/', '/api/v1/status']

f_path = '/api/v1/status'

for path in excluded_paths:
    if re.match(path, f_path):
        print('match', path)
    else:
        print('No match for', path)
