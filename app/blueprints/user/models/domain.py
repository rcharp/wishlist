from sqlalchemy import or_

from werkzeug.security import generate_password_hash, check_password_hash
from lib.util_sqlalchemy import ResourceMixin, AwareDateTime
from app.extensions import db


class Domain(ResourceMixin, db.Model):

    __tablename__ = 'domains'

    # Objects.
    id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.BigInteger, unique=True, index=True, nullable=False)
    name = db.Column(db.String(255), unique=True, index=True, nullable=True, server_default='')
    company = db.Column(db.String(255), unique=False, index=True, nullable=True, server_default='')
    admin_email = db.Column(db.String(255), unique=False, index=True, nullable=True, server_default='')
    private_key = db.Column(db.String(128), nullable=False, server_default='')

    # Relationships.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'),
                           index=True, nullable=True, primary_key=False, unique=False)

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(Domain, self).__init__(**kwargs)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    def find_by_id(cls, identity):
        """
        Find an email by its message id.

        :param identity: Email or username
        :type identity: str
        :return: User instance
        """
        return Domain.query.filter(
          (Domain.id == identity).first())

    @classmethod
    def search(cls, query):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        if not query:
            return ''

        search_query = '%{0}%'.format(query)
        search_chain = (Domain.id.ilike(search_query))

        return or_(*search_chain)

    @classmethod
    def bulk_delete(cls, ids):
        """
        Override the general bulk_delete method because we need to delete them
        one at a time while also deleting them on Stripe.

        :param ids: Domain of ids to be deleted
        :type ids: domain
        :return: int
        """
        delete_count = 0

        for id in ids:
            domain = Domain.query.get(id)

            if domain is None:
                continue

            domain.delete()

            delete_count += 1

        return delete_count

    @classmethod
    def encrypt(cls, plaintext_password):
        """
        Hash a plaintext string using PBKDF2. This is good enough according
        to the NIST (National Institute of Standards and Technology).

        In other words while bcrypt might be superior in practice, if you use
        PBKDF2 properly (which we are), then your passwords are safe.

        :param plaintext_password: Password in plain text
        :type plaintext_password: str
        :return: str
        """
        if plaintext_password:
            return generate_password_hash(plaintext_password)

        return None

    def authenticated(self, with_password=True, key=''):
        """
        Ensure a user is authenticated, and optionally check their password.

        :param with_password: Optionally check their password
        :type with_password: bool
        :param key: Optionally verify this as their password
        :type key: str
        :return: bool
        """
        if with_password:
            return check_password_hash(self.private_key, key)

        return True
