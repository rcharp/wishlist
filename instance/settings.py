import os
from celery.schedules import crontab

PASSWORD = 'hyrule724'

PRODUCTION = False

DOMAIN = 'getwishlist.io'
IP_ADDRESS = '192.168.0.1'

MAIL_USERNAME = 'ricky@getwishlist.io'
MAIL_PASSWORD = 'hyrule724'
MAIL_DEFAULT_SENDER = 'ricky@getwishlist.io'
MAIL_SERVER = 'box487.bluehost.com'
MAIL_PORT = 465
MAIL_USE_SSL = True

STRIPE_TEST_SECRET_KEY = 'sk_test_z8b7KkWi2P3M71sDjOl3VyM6'
STRIPE_TEST_PUBLISHABLE_KEY = 'pk_test_DX6xHgQH53sA1l78sasUZ9gA'
STRIPE_SECRET_KEY = 'sk_live_ZaH24Fv0QMw66ptWVYrqWy0k'
STRIPE_PUBLISHABLE_KEY = 'pk_live_Nwbqc3RiygVrl3aRrPSnG0Jj'

STRIPE_KEY = STRIPE_TEST_SECRET_KEY

SQLALCHEMY_DATABASE_URI = 'postgres://zrbkyutzecevbk:c07c9ee458d51774365e661a461781d4a81e61b3afd2b566b0ca3c0eab8e660c@ec2-34-232-147-86.compute-1.amazonaws.com:5432/d8k1djg98f27q4'

CARD_NAME = 'Ricky Charpentier'
CARD_NUMBER = '4242424242424242'
CARD_MONTH = '01'
CARD_YEAR = '2020'
CARD_CVV = '123'

# *********************** These are the only values that matter, ignore the ones below ****************************
CACHE_REDIS_URL = 'redis://redis:6379/0'
CLOUDAMPQ_URL = 'amqp://kbquxflb:CPARPy56veNcIRQJfzQbWXHDklSHjGXI@fox.rmq.cloudamqp.com/kbquxflb'

# Cache
CACHE_TYPE = 'redis'
CACHE_REDIS_HOST = 'ec2-3-225-119-109.compute-1.amazonaws.com'
CACHE_REDIS_PASSWORD = 'pc41e2374a26232c587b3fbacb3cba12b4f9555f9a6227ed30dbf89b4f2cb8965'
CACHE_DEFAULT_TIMEOUT = 86400
CACHE_REDIS_PORT = 10859

# Celery.
CELERY_BROKER_URL = CACHE_REDIS_URL
CELERY_BROKER_HEARTBEAT = 10
CELERY_BROKER_HEARTBEAT_CHECKRATE = 2
CELERY_RESULT_BACKEND = CACHE_REDIS_URL
CELERY_REDIS_URL = CACHE_REDIS_URL
CELERY_REDIS_HOST = CACHE_REDIS_HOST
CELERY_REDIS_PORT = CACHE_REDIS_PORT
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_EXPIRES = 300
CELERY_REDIS_MAX_CONNECTIONS = 20

# Celery Heartbeat.
BROKER_HEARTBEAT = 10
BROKER_HEARTBEAT_CHECKRATE = 2

# Celery schedule
CELERYBEAT_SCHEDULE = {
    # 'dropping_domains': {
    #     'task': 'app.blueprints.api.tasks.generate_drops',
    #     'schedule': crontab(hour=0, minute=0)
    #     # 'schedule': crontab(minute="*/1")
    # }
}

# SqlAlchemy.
SQLALCHEMY_USER = 'hjsdnvzoaowxxq'
SQLALCHEMY_DATABASE = 'dci1arg0ud6cnk'
SQLALCHEMY_HOST = 'ec2-34-233-186-251.compute-1.amazonaws.com'
SQLALCHEMY_PASSWORD = '152e5668140702d33d6a7162c71f90bd3cb56871a170de76cd13ce8fee3e330d'
SQLALCHEMY_POOL_RECYCLE = 499
SQLALCHEMY_POOL_TIMEOUT = 120

# User
SEED_ADMIN_EMAIL = 'ricky@getwishlist.io'
SEED_ADMIN_USERNAME = 'admin'
SEED_MEMBER_EMAIL = 'rickycharpentier@gmail.com'
SEED_MEMBER_USERNAME = 'ricky'
SEED_TEST_EMAIL = 'head2dasky@gmail.com'
SEED_ADMIN_PASSWORD = 'hyrule724'

SEED_CUSTOMER_ID = 'cus_Gpvj1EwzERfYxe'

SERVER_NAME = 'localhost:5000'
SECRET_KEY = 'hyrule724'
CRYPTO_KEY = '1MQkYzBdtbrul6-luLdpLPuOCosCLbADga6mQZACCZ0='

# Mailerlite
MAILERLITE_API_KEY = 'ddd236782e686e86c817ddffe98eb43e'

# GoDaddy API
GODADDY_TEST_API_KEY = '3mM44UagnkLxsY_DJuPuH1WUnfJ3sKmp8GUaB'
GODADDY_TEST_SECRET_KEY = 'AZCam4zCnpFrUUJj4oUJL'
GODADDY_API_KEY = 'dKD3AoCHdJL2_Fjb6ePi8EnmXN1HTaQCxJQ'
GODADDY_SECRET_KEY = 'D8XFiLuxSv7ey7xbyFuGT2'

# Heroku
HEROKU_API_KEY = '0c2df769-8f51-4f92-a599-2ec8403a0da1'
HEROKU_TOKEN = 'd9b197ed-8516-4338-a0f9-30deb57f9c1c'

# Cloudflare
CLOUDFLARE_TOKEN = 'qeOBZAqH90O2fpuOUwDAVeqM-_YMjIOkeBkvgov4'