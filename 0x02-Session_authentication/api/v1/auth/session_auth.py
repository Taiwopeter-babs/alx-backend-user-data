#!/usr/bin/env python3
"""
Session Authentication module
"""
from api.v1.auth.auth import Auth
# import base64
# import binascii
from typing import Tuple, TypeVar, Union
import uuid


class SessionAuth(Auth):
    """
    Implements Session Authentication
    """
    user_id_by_session_id = {}

    def create_session(self, user_id: Union[str, None] = None) -> str:
        """
        Creates a `session_id` for a user based on `user_id`
        """
        if user_id is None or not isinstance(user_id, str):
            return None

        # Generate new session id
        new_session_id = str(uuid.uuid4())
        self.user_id_by_session_id[new_session_id] = user_id

        return new_session_id

    def user_id_for_session_id(self,
                               session_id: Union[str, None] = None
                               ) -> str:
        """
        Returns a `user_id` based on a `session_id`
        """
        if session_id is None or not isinstance(session_id, str):
            return None

        return self.user_id_by_session_id.get(session_id, None)

    def current_user(self, request=None) -> Union[None, TypeVar('User')]:
        """
        returns a `User` instance based on the cookie `_my_session_id` value
        """
        from models.user import User

        if request is None:
            return None

        # get cookie value
        cookie_value_session_id = self.session_cookie(request)

        # get user_id from storage based on the session_id
        cookie_user_id = self.user_id_for_session_id(cookie_value_session_id)
        if cookie_user_id is None:
            return None

        # get user from storage
        return User.get(cookie_user_id)

    def destroy_session(self, request=None) -> bool:
        """
        deletes a session_id from storage
        """
        if request is None:
            return False

        user_session_id = self.session_cookie(request)
        if user_session_id is None:
            return False

        # check for session_id value in storage
        if self.user_id_for_session_id(user_session_id) is None:
            return False
        # delete session id from storage
        del self.user_id_by_session_id[user_session_id]

        return True
