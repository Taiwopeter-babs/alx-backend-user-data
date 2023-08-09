#!/usr/bin/env python3
"""
Authentication module
"""
from flask import request
import os
import re
from typing import List, TypeVar, Union


class Auth:
    """
    Authentication class
    """

    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """
        Returns a boolean value for a path.\n
        `excluded_paths` can contain a regular expression string
        `/api/v1/stat*`
            - The routes `/api/v1/status/` and `/api/v1/stats` will match\n
        Return:
          - True if the `path` is not in `excluded_paths`; requires auth
          - False if the `path` is in `excluded_paths`; no auth required
        """
        if path is None:
            return True
        if excluded_paths is None or len(excluded_paths) == 0:
            return True

        # check path string for `/`
        if path[-1] != '/':
            path = path + '/'

        # check for pattern match of path
        for ex_path in excluded_paths:
            if re.match(ex_path, path):
                return False

        return True

    def authorization_header(self,
                             request=None
                             ) -> Union[str, None]:
        """
        returns authorization header value
        """
        if request is None:
            return None
        if request.headers.get('Authorization') is None:
            return None

        return request.headers.get('Authorization')

    def current_user(self,
                     request=None
                     ) -> Union[None, TypeVar('User')]:
        """
        Returns a current user
        """
        return None

    def session_cookie(self, request=None) -> str:
        """
        returns the value of cookie `_my_session_id`.
        - The name of the cookie is stored in the environment variable
            `SESSION_NAME`.
        """
        if request is None:
            return None

        cookie_name = os.getenv('SESSION_NAME')
        # get cookie from request
        cookie_value = request.cookies.get(cookie_name)
        return cookie_value
