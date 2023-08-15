#!/usr/bin/env python3
"""Hash passwords"""
import bcrypt
from db import DB
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
import uuid
from typing import TypeVar, Union


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        """Instantiation method"""
        self._db = DB()

    def _hash_password(self, password: str) -> bytes:
        """returns a hashed string of a password"""
        # convert sting to bytes
        encoded = password.encode('utf-8')

        hashed = bcrypt.hashpw(encoded, bcrypt.gensalt())
        return hashed

    def register_user(self, email: str, password: str) -> TypeVar('User'):
        """
        Registers a new user
        """
        # check if user already exists
        try:
            user = self._db.find_user_by(email=email)
            if user:
                raise ValueError('User {} already exists'.format(email))

        except NoResultFound:
            # hash password and save to storage
            hashed_pwd = self._hash_password(password)
            new_user = self._db.add_user(email, hashed_pwd)

        return new_user

    def valid_login(self, email: str, password: str) -> bool:
        """
        Validates a user's credentials
        """
        # check for user's existence
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return False

        # convert sting to bytes
        encoded = password.encode('utf-8')

        return bcrypt.checkpw(encoded, user.hashed_password)

    def _generate_uuid(self) -> str:
        """Generate a uuid"""
        return str(uuid.uuid4())

    def create_session(self, email: str) -> Union[str, None]:
        """
        creates a new session id for a user
        """
        try:
            user = self._db.find_user_by(email=email)
            # generate a session id
            session_id = self._generate_uuid()

            self._db.update_user(user.id, session_id=session_id)
        except (NoResultFound, ValueError):
            return None

        return session_id

    def destroy_session(self, user_id: int) -> None:
        """
        removes a session id from user
        """
        try:
            user = self._db.find_user_by(id=user_id)
        except NoResultFound:
            raise
        self._db.update_user(user.id, session_id=None)

        return None

    def get_user_from_session_id(self,
                                 session_id: str
                                 ) -> Union[None, TypeVar('User')]:
        """
        get user by session id
        """
        if session_id is None:
            return None

        try:
            user = self._db.find_user_by(session_id=session_id)
        except (NoResultFound, ValueError):
            return None

        return user

    def get_reset_password_token(self, email: str) -> str:
        """
        Generate password reset token for a user
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            raise ValueError
        reset_token = str(uuid.uuid4())

        # update user's reset_token field
        self._db.update_user(user.id, reset_token=reset_token)

        return reset_token

    def update_password(self, reset_token: str, password: str) -> None:
        """
        Updates a user password
        """
        if reset_token is None or password is None:
            raise ValueError

        try:
            user = self._db.find_user_by(reset_token=reset_token)
        except NoResultFound:
            raise ValueError

        # hash user's new password
        hashed_password = self._hash_password(password)
        # update fields
        kwargs = {
            "hashed_password": hashed_password,
            "reset_token": None
        }
        self._db.update_user(user.id, **kwargs)
        return None
