#!/usr/bin/env python3
"""Hash passwords"""
import bcrypt


def hash_password(password: str) -> bytes:
    """returns a hashed string of a password"""
    # convert sting to bytes
    encoded = password.encode('utf-8')

    hashed = bcrypt.hashpw(encoded, bcrypt.gensalt())
    return hashed


def is_valid(hashed_password: bytes, password: str) -> bool:
    """checks the validity of a hashed password"""
    # convert sting to bytes
    encoded = password.encode('utf-8')

    return bcrypt.checkpw(encoded, hashed_password)
