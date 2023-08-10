#!/usr/bin/env python3
"""
Session Expiration authentication module
"""
from api.v1.auth.session_auth import SessionAuth
from datetime import datetime, timedelta
import os
from typing import Union


class SessionExpAuth(SessionAuth):
    """
    Implements Session Expiration Authentication
    """

    def __init__(self):
        """Instantiation and Implements Session Expiration Authentication"""
        session_duration = os.getenv('SESSION_DURATION')
        try:
            self.session_duration = int(session_duration)
        except (ValueError, TypeError):
            self.session_duration = 0

    def create_session(self,
                       user_id: Union[str, None] = None
                       ) -> Union[str, None]:
        """
        Creates session id
        """
        session_id = super().create_session(user_id)
        if session_id is None:
            return None
        # initialize session_id to a dict
        self.user_id_by_session_id[session_id] = {}
        # set user_id and current date
        self.user_id_by_session_id[session_id]['user_id'] = user_id
        self.user_id_by_session_id[session_id]['created_at'] = datetime.now()

        return session_id

    def user_id_for_session_id(self,
                               session_id: Union[str, None] = None
                               ) -> str:
        """
        returns a `user_id` from a `session_id` dictionary if the
        session is still valid and not expired:\n
        `created_at + self.session_duration < current_date`.\n
        If the above is true, it means the session is expired.
        """
        if session_id is None:
            return None
        session_dict = self.user_id_by_session_id.get(session_id)
        if session_dict is None:
            return None
        # check session duration
        if self.session_duration <= 0:
            return session_dict.get('user_id')
        if session_dict.get('created_at', None) is None:
            return None

        # check if the session already expired
        if session_dict.get('created_at') + \
                timedelta(seconds=self.session_duration) \
                < datetime.now():
            return None

        return session_dict.get('user_id')
