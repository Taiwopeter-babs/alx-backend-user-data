#!/usr/bin/env python3
"""
'|' in regex means `OR`; A|B where A and B are regex patterns.
The function `filter_datum` creates regex patterns for each field in
the list, and joins the results.
"""
import os
import re
import logging
import mysql.connector
from mysql.connector.connection import MySQLConnection
from typing import Any, List

# regex pattern
pat = '(?<={}=)[^{}]*(?={})'

# PII (Personal Identifiable Info) fields
PII_FIELDS = ('name', 'email', 'phone', 'ssn', 'password')


def filter_datum(fields: List[str], redaction: str, message: str,
                 separator: str) -> str:
    """Hides values of fields with redaction string"""
    return re.sub('|'.join(pat.format(field, separator, separator)
                           for field in fields), redaction, message)


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
    """

    REDACTION: str = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """filter log records"""
        log_msg = super(RedactingFormatter, self).format(record)
        return filter_datum(self.fields, self.REDACTION,
                            log_msg, self.SEPARATOR)


def get_logger() -> logging.Logger:
    """creates and returns a logger"""
    # create logger and set level
    logger = logging.getLogger('user_data')
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # set handler and add formatter
    formatter = RedactingFormatter(list(PII_FIELDS))
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # add handler to logger object
    logger.addHandler(stream_handler)

    return logger


def get_db() -> MySQLConnection:
    """returns a mysql connector"""
    USERNAME = 'root' if not os.getenv(
        'PERSONAL_DATA_DB_USERNAME') else os.getenv(
        'PERSONAL_DATA_DB_USERNAME')
    PASSWORD = "" if not os.getenv(
        'PERSONAL_DATA_DB_PASSWORD') else os.getenv(
        'PERSONAL_DATA_DB_PASSWORD')
    HOST = 'localhost' if not os.getenv(
        'PERSONAL_DATA_DB_HOST') else os.getenv('PERSONAL_DATA_DB_HOST')
    DB_NAME = os.getenv('PERSONAL_DATA_DB_NAME')

    connector = mysql.connector.connect(
        host=HOST,
        port=3306,
        user=USERNAME,
        password=PASSWORD,
        database=DB_NAME
    )

    return connector


def main() -> None:
    """main entry"""
    db = get_db()
    logger = get_logger()

    # get cursor and execute the query
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")

    # get all the rows and column names
    rows = cursor.fetchall()
    result_fields = cursor.column_names

    for row in rows:
        row_str = ''
        for col_name, row_name in zip(result_fields, row):
            row_str += "{}={};".format(col_name, row_name)
        logger.info(row_str)


if __name__ == '__main__':
    main()
