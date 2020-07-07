from flask_wtf import Form
from wtforms import HiddenField, StringField, PasswordField
from wtforms.validators import DataRequired, Length, Optional, Regexp, EqualTo
from wtforms_components import EmailField, Email
from wtforms_alchemy import Unique

from lib.util_wtforms import ModelForm
from app.blueprints.user.models.user import User, db
from app.blueprints.user.validations import ensure_identity_exists, \
    ensure_existing_password_matches


class LoginForm(Form):
    next = HiddenField()
    identity = StringField('Username or email',
                           [DataRequired(), Length(3, 254)])
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])
    # remember = BooleanField('Stay signed in')


class LoginFormAnon(Form):
    next = HiddenField()
    identity = StringField('Username or email',
                           [DataRequired(), Length(3, 254)])
    domain = StringField('Domain (optional)')
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])
    # remember = BooleanField('Stay signed in')


class BeginPasswordResetForm(Form):
    identity = StringField('Username or email',
                           [DataRequired(),
                            Length(3, 254),
                            ensure_identity_exists])


class PasswordResetForm(Form):
    reset_token = HiddenField()
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])


class SignupForm(ModelForm):
    name = StringField(validators=[
        DataRequired()
    ])

    email = EmailField(validators=[
        DataRequired(),
        Email(),
        Unique(User.email, get_session=lambda: db.session, message='This email is already in use. Login instead?')
    ])

    password = PasswordField('Password', [DataRequired(), Length(8, 128)])
    # confirm = PasswordField("Repeat Password", [DataRequired(), EqualTo("password", message="Passwords don't match!"), Length(8, 128)])


class SignupFormAnon(ModelForm):
    name = StringField(validators=[
        DataRequired()
    ])

    email = EmailField(validators=[
        DataRequired(),
        Email(),
        Unique(User.email, get_session=lambda: db.session, message='This email is already in use. Login instead?')
    ])

    company = StringField(validators=[
        DataRequired()
    ])

    domain = StringField(validators=[
        DataRequired(),
        Regexp('^[A-Za-z]+$', message='Only letters are allowed for domain names.'),
    ])

    password = PasswordField('Password', [DataRequired(), Length(8, 128)])
    # confirm = PasswordField("Repeat Password", [DataRequired(), EqualTo("password", message="Passwords don't match!"), Length(8, 128)])


class WelcomeForm(ModelForm):
    username_message = 'Letters, numbers and underscores only please.'

    username = StringField(validators=[
        Unique(
            User.username,
            get_session=lambda: db.session
        ),
        DataRequired(),
        Length(1, 16),
        Regexp('^\w+$', message=username_message)
    ])


class UpdateCredentials(ModelForm):
    current_password = PasswordField('Current password',
                                     [DataRequired(),
                                      Length(8, 128),
                                      ensure_existing_password_matches])

    email = EmailField(validators=[
        Email(),
        Unique(
            User.email,
            get_session=lambda: db.session
        )
    ])

    name = StringField('Full name')

    username = StringField(validators=[
        Unique(
            User.username,
            get_session=lambda: db.session,
            message='That username is already in use.'
        )
    ])

    password = PasswordField('New Password', [Optional(), Length(8, 128)])
    confirm = PasswordField("Repeat New Password", [EqualTo("password", message="Passwords don't match")])
