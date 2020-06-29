__author__ = 'Ricky'
from flask import Flask, render_template
from flask_mail import Mail, Message
from app.app import create_celery_app

celery = create_celery_app()


def send_welcome_email(email):
    app = Flask(__name__)
    mail = Mail()
    mail.init_app(app)
    msg = Message("You've successfully signed up for GetWishlist.io!",
                  sender="support@getwishlist.io",
                  recipients=[email])

    msg.html = render_template('user/mail/welcome_email.html')

    mail.send(msg)


def send_reservation_email(email, domain, available):
    app = Flask(__name__)
    mail = Mail()
    mail.init_app(app)
    msg = Message("You've successfully reserved " + domain + "!",
                  sender="support@getwishlist.io",
                  recipients=[email])
    msg.html = render_template('user/mail/reservation_email.html', domain=domain, available=available)

    response = Message("User " + email + " reserved " + domain + ".",
                       recipients=["support@getwishlist.io"],
                       sender="support@getwishlist.io")

    response.body = email + " reserved the following domain:\n\n" + domain + ".\n\nIt's available on " + available + "."

    mail.send(msg)
    mail.send(response)


def send_secured_email(email, domain):
    app = Flask(__name__)
    mail = Mail()
    mail.init_app(app)
    msg = Message("We successfully secured " + domain + " for you!",
                  sender="support@getwishlist.io",
                  recipients=[email])
    msg.html = render_template('user/mail/secured_domain.html', domain=domain)

    mail.send(msg)


def send_temp_password_email(email, password, domain):
    app = Flask(__name__)
    mail = Mail()
    mail.init_app(app)
    msg = Message("Your temporary password for Wishlist",
                  sender="support@getwishlist.io",
                  recipients=[email])
    msg.html = render_template('user/mail/temp_password_email.html', password=password, domain=domain)

    mail.send(msg)

    print("Set email")


def contact_us_email(email, message):
    app = Flask(__name__)
    mail = Mail()
    mail.init_app(app)
    msg = Message("[GetWishlist.io Contact] Support request from " + email,
                  recipients=["support@getwishlist.io"],
                  sender="support@getwishlist.io",
                  reply_to=email)
    msg.body = email + " sent you a message:\n\n" + message

    response = Message("Your email to GetWishlist.io has been received.",
                       recipients=[email],
                       sender="support@getwishlist.io")

    response.html = render_template('user/mail/contact_email.html',email=email, message=message)

    mail.send(msg)
    mail.send(response)


def send_cancel_email(email):
    app = Flask(__name__)
    mail = Mail()
    mail.init_app(app)
    msg = Message("Goodbye from GetWishlist.io",
                  sender="support@getwishlist.io",
                  recipients=[email])

    msg.html = render_template('user/mail/cancel_email.html')

    mail.send(msg)
