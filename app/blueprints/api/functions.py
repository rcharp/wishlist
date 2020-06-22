import jwt
import os
from flask import current_app


# Tokens ###########################################
'''
Create a token for the user using JWT
'''


def create_user_token(user, key):
    user = {
        'email': user.email,
        'id': user.id,
        'name': user.name,
    }
    return jwt.encode(user, key, algorithm='HS256')


'''
Decrypt the passed user token using JWT
'''


def decrypt_user_token(token, key):
    return jwt.decode(token, key, verify=True)


'''
Create a general token for plaintext
'''


def serialize_token(plaintext):
    data = {
        'value': plaintext
    }
    return jwt.encode(data, os.environ.get('SECRET_KEY'), algorithm='HS256')


'''
Deserialize a token
'''


def deserialize_token(token):
    return jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=['HS256'], verify=True)


def encrypt(plaintext):
    from cryptography.fernet import Fernet
    message = plaintext.encode()

    f = Fernet(current_app.config['SECRET_KEY'])
    return f.encrypt(message)


def decrypt(encrypted):
    from cryptography.fernet import Fernet

    f = Fernet(current_app.config['SECRET_KEY'])
    return f.decrypt(encrypted)

