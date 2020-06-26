from sqlalchemy import or_

from lib.util_sqlalchemy import ResourceMixin, AwareDateTime
from app.extensions import db


class Comment(ResourceMixin, db.Model):

    __tablename__ = 'comments'

    # Objects.
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, unique=True, index=True, nullable=False)
    comment = db.Column(db.UnicodeText, unique=False, index=True, nullable=True, server_default='')
    fullname = db.Column(db.String(255), unique=False, index=True, nullable=True, server_default='')

    # Relationships.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'),
                           index=True, nullable=True, primary_key=False, unique=False)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.feedback_id', onupdate='CASCADE', ondelete='CASCADE'),
                        index=True, nullable=True, primary_key=False, unique=False)
    domain_id = db.Column(db.BigInteger, db.ForeignKey('domains.domain_id', onupdate='CASCADE', ondelete='CASCADE'),
                            index=True, nullable=True, primary_key=False, unique=False)
    parent_id = db.relation('Comment', remote_side=[comment_id], primaryjoin="comments.parent_id==comments.comment_id")

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(Comment, self).__init__(**kwargs)

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
        return Comment.query.filter(
          (Comment.id == identity).first())

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
        search_chain = (Comment.id.ilike(search_query))

        return or_(*search_chain)

    @classmethod
    def bulk_delete(cls, ids):
        """
        Override the general bulk_delete method because we need to delete them
        one at a time while also deleting them on Stripe.

        :param ids: Comment of ids to be deleted
        :type ids: comment
        :return: int
        """
        delete_count = 0

        for id in ids:
            comment = Comment.query.get(id)

            if comment is None:
                continue

            comment.delete()

            delete_count += 1

        return delete_count
