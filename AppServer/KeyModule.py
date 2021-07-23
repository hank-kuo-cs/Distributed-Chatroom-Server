import string
import random
from DB_Broker import *


def is_token(s):
    # Check that the string whether matches the token format
    if len(s) != 36 or s[8] != '-' or s[13] != '-' or s[18] != '-' or s[23] != '-':
        return False

    return True


def token_generator(size=32):
    # Generate a token composed with lowercase and digits
    # Default size is 32, and the format is 8-4-4-12
    # Check all user records' TOKEN to ensure this token is unique

    chars = string.ascii_lowercase + string.digits

    users = send_sql_command(func='select_users', keys=[], datas=[])

    tell = True

    while True:
        token = ''.join(random.choices(chars, k=size))
        token = token[:8] + '-' + token[8:12] + '-' + token[12:16] + '-' + token[16:20] + '-' + token[20:]

        if users:
            for u in users:
                if token == u.token:
                    tell = False
                    break

            if tell is False:
                tell = True
                continue

        break

    return token


def guid_generaotor(size=32):
    # Generate a guid composed with lowercase and digits
    # Check all user records' GUID to ensure the guid is unique
    # Default size is 32
    chars = string.ascii_lowercase + string.digits

    users = send_sql_command(func='select_users', keys=[], datas=[])

    tell = True

    while True:
        guid = ''.join(random.choices(chars, k=size))

        if users:
            for u in users:
                if guid == u.guid:
                    tell = False
                    break

            if tell is False:
                tell = True
                continue

        break

    return guid
