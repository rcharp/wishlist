import jwt


def create_token():
    private_key = 'YOUR_PRIVATE_SSO_KEY'
    user_data = {
        'email': 'test@gmail.com',
        'id': 'test_id',
        'name': 'test_name',
    }
    return jwt.encode(user_data, private_key, algorithm='HS256')


def decrypt_token():
    token = create_token()
    return jwt.decode(token, 'YOUR_PRIVATE_SSO_KEY', verify=True)

