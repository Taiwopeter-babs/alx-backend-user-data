#!/usr/bin/env python3
"""
Authentication module
"""
from flask import request, Request
from typing import List, TypeVar, Union


class Auth:
    """
    Authentication class
    """

    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """
        Returns a boolean value for a path.\n
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

        if path in excluded_paths:
            return False

        return True

    def authorization_header(self,
                             request: Union[Request, None] = None
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
                     request: Union[Request, None] = None
                     ) -> Union[None, TypeVar('User')]:
        """
        Returns a current user
        """
        return None
