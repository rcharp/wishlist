from sqlalchemy import or_

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
    def serialize_private_key(cls, plaintext):
        """
        Hash a plaintext string using PBKDF2. This is good enough according
        to the NIST (National Institute of Standards and Technology).

        In other words while bcrypt might be superior in practice, if you use
        PBKDF2 properly (which we are), then your passwords are safe.

        :param plaintext: Password in plain text
        :type plaintext: str
        :return: str
        """
        if plaintext:
            from app.blueprints.api.functions import serialize_token
            return serialize_token(plaintext)

        return None

    @classmethod
    def deserialize_private_key(cls, token):
        """
        Hash a plaintext string using PBKDF2. This is good enough according
        to the NIST (National Institute of Standards and Technology).

        In other words while bcrypt might be superior in practice, if you use
        PBKDF2 properly (which we are), then your passwords are safe.

        :param plaintext: Password in plain text
        :type plaintext: str
        :return: str
        """
        if token:
            from app.blueprints.api.functions import deserialize_token
            return deserialize_token(token)

        return None
