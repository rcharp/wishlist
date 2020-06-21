import jwt


def create_token(user, key):
    user_data = {
        'email': user.email,
        'id': user.id,
        'name': user.name,
    }
    return jwt.encode(user_data, key, algorithm='HS256')


def decrypt_token(token, key):
    return jwt.decode(token, key, verify=True)

