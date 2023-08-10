#!/usr/bin/env python3
"""
Session Database Expiration authentication module
"""
from api.v1.auth.session_exp_auth import SessionExpAuth
from datetime import datetime, timedelta
from models.user_session import UserSession
from typing import Union


class SessionDBAuth(SessionExpAuth):
    """
    Session Expiration Database Authentication class
    """

    def __init__(self):
        """Instantiation method"""
        super().__init__()

    def create_session(self,
                       user_id: Union[str, None] = None
                       ) -> Union[str, None]:
        """
        Creates a new `UserSession` instance session id
        """
        session_id = super().create_session(user_id)
        if session_id is None:
            return None
        # create a new UserSession
        _dict = {"user_id": user_id, "session_id": session_id}
        user_session = UserSession(**_dict)
        user_session.save()

        return session_id

    def user_id_for_session_id(self,
                               session_id: Union[str, None] = None
                               ) -> Union[str, None]:
        """
        returns a `UserSession`'s user_id from the `database` based
        on the `session_id`
        """
        if session_id is None:
            return None
        # define the search
        _objs = UserSession.search({"session_id": session_id})
        if len(_objs) == 0:
            return None
        user_session_obj = _objs[0]

        # check session duration
        if self.session_duration <= 0:
            return user_session_obj.user_id

        # check if the session already expired
        if user_session_obj.created_at + \
                timedelta(seconds=self.session_duration) \
                < datetime.now():
            return None

        return user_session_obj.user_id

    def destroy_session(self, request=None) -> bool:
        """
        deletes a 'UserSession' instance/instances from storage
        based on the session_id in the cookie
        """
        if request is None:
            return False

        # get session_id from request cookie
        session_id = self.session_cookie(request)
        if session_id is None:
            return False
        # get user sessions from database
        # define the search
        _objs = UserSession.search({"session_id": session_id})
        if len(_objs) == 0:
            return False
        # remove all session objects from database
        for user_session_obj in _objs:
            user_session_obj.remove()
        return True
