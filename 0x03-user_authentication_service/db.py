"""DB module
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from typing import Mapping, Tuple, TypeVar

from user import Base, User


class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db")
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> TypeVar('User'):
        """
        Adds a new user to the storage
        """
        new_dict = {
            "email": email,
            "hashed_password": hashed_password
        }
        new_user = User(**new_dict)
        self._session.add(new_user)
        self._session.commit()

        return new_user

    def find_user_by(self, **kwargs: Mapping) -> Tuple:
        """
        finds a user by using arbitary key-value args
        """
        try:
            user_obj = self._session.query(
                User).filter_by(**kwargs).first()

            # raise Not Found Error
            if user_obj is None:
                raise NoResultFound
        except (InvalidRequestError, NoResultFound):
            raise
        return user_obj

    def update_user(self, user_id: int, **kwargs: Mapping) -> None:
        """
        Updates a user object
        """
        user_obj = self.find_user_by(id=user_id)

        try:
            for col_name, value in kwargs.items():
                setattr(user_obj, col_name, value)
        except InvalidRequestError:
            raise ValueError
        self._session.commit()
        return None
