#!/usr/bin/env python3
"""
Basic Access Authentication module
"""
from api.v1.auth.auth import Auth
import base64
import binascii
from typing import Tuple, TypeVar, Union


class BasicAuth(Auth):
    """
    Implements Basic Access Authentication
    """

    def extract_base64_authorization_header(
        self,
        authorization_header: Union[None, str]
    ) -> Union[None, str]:
        """
        returns the base64 encoded string of the authorization header
        """
        if authorization_header is None:
            return None
        if not isinstance(authorization_header, str):
            return None

        # Authorization header should be separated by one space
        if authorization_header.split(' ')[0] != 'Basic' \
                or authorization_header.split(' ')[1] == '':
            return None

        return authorization_header.split(' ')[1]

    def decode_base64_authorization_header(
            self,
            base64_authorization_header: Union[None, str]
    ) -> Union[None, str]:
        """
        returns the base64 decoded string of the authorization header
         - `Authorization: Basic hfhhr8885853jj==`\n
            `hfhhr8885853jj==` is decoded and returned
        """
        if base64_authorization_header is None:
            return None
        if not isinstance(base64_authorization_header, str):
            return None

        try:
            decoded_str = base64.b64decode(
                base64_authorization_header).decode('UTF-8')
        except (UnicodeDecodeError, binascii.Error):
            return None

        return decoded_str

    def extract_user_credentials(
            self,
            decoded_base64_authorization_header: Union[None, str]
    ) -> Union[Tuple[None, None], Tuple[str, str]]:
        """
        returns the user email and password from the decoded `Authorization`
        header.
        The decoded string is `email:password`
            - `password` can contain the `:` character
        """
        none_value = (None, None)

        if decoded_base64_authorization_header is None:
            return none_value
        if not isinstance(decoded_base64_authorization_header, str):
            return none_value

        if ':' not in decoded_base64_authorization_header:
            return none_value

        email, password = decoded_base64_authorization_header.split(':', 1)
        if not email or not password:
            return none_value

        return (email, password)

    def user_object_from_credentials(self,
                                     user_email: Union[None, str],
                                     user_pwd: Union[str, None]
                                     ) -> Union[None, TypeVar('User')]:
        """
        returns a user object based on the email and password
        """
        from models.user import User

        if user_email is None or not isinstance(user_email, str):
            return None
        if user_pwd is None or not isinstance(user_pwd, str):
            return None

        if User.count() == 0:
            return None

        _objs = User.search({"email": user_email})
        if len(_objs) == 0:
            return None
        # initialize user instance
        user_obj = _objs[0]
        # validate user password
        if not user_obj.is_valid_password(user_pwd):
            return None

        return user_obj

    def current_user(self,
                     request=None
                     ) -> Union[None, TypeVar('User')]:
        """
        Returns a current user of object `User`
        """
        if request is None:
            return None

        # get the value of the authorization header
        auth_header = self.authorization_header(request)
        if auth_header is None:
            return None
        # extract the encoded str
        encoded_str = self.extract_base64_authorization_header(auth_header)
        if encoded_str is None:
            return None

        # decode the encoded string of the header
        decoded_str = self.decode_base64_authorization_header(encoded_str)
        if decoded_str is None:
            return None

        # extract user credentials from the decoded str
        email, password = self.extract_user_credentials(decoded_str)
        if email is None and password is None:
            return None

        # returns a user object or None
        return self.user_object_from_credentials(email, password)
