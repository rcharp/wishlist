from flask import (
    Blueprint,
    redirect,
    request,
    flash,
    Markup,
    url_for,
    render_template,
    current_app,
    json,
    jsonify,
    session)
from flask_login import (
    login_required,
    login_user,
    current_user,
    logout_user)

import time
import random
from operator import attrgetter
from flask_cors import cross_origin

from lib.safe_next_url import safe_next_url
from app.blueprints.user.decorators import anonymous_required
from app.blueprints.user.models.user import User, Domain
from app.blueprints.user.forms import (
    LoginForm,
    BeginPasswordResetForm,
    PasswordResetForm,
    SignupForm,
    WelcomeForm,
    UpdateCredentials)

from app.extensions import cache, csrf, timeout, db
from importlib import import_module
from sqlalchemy import or_, and_, exists, inspect, func
from app.blueprints.billing.charge import (
    get_card
)
from app.blueprints.billing.models.customer import Customer
from app.blueprints.api.models.feedback import Feedback
from app.blueprints.api.models.status import Status
from app.blueprints.api.models.workspace import Workspace

user = Blueprint('user', __name__, template_folder='templates')


# Login and Credentials -------------------------------------------------------------------
@user.route('/login', methods=['GET', 'POST'])
@anonymous_required()
@csrf.exempt
def login():

    # This redirects to the link that the button was sending to before login
    form = LoginForm(next=request.args.get('next'))

    # This redirects to dashboard always.
    # form = LoginForm(next=url_for('user.dashboard'))

    if form.validate_on_submit():

        u = User.find_by_identity(request.form.get('identity'))

        if u and u.is_active() and u.authenticated(password=request.form.get('password')):
            # As you can see remember me is always enabled, this was a design
            # decision I made because more often than not users want this
            # enabled. This allows for a less complicated login form.
            #
            # If however you want them to be able to select whether or not they
            # should remain logged in then perform the following 3 steps:
            # 1) Replace 'True' below with: request.form.get('remember', False)
            # 2) Uncomment the 'remember' field in user/forms.py#LoginForm
            # 3) Add a checkbox to the login form with the id/name 'remember'
            if login_user(u, remember=True) and u.is_active():
                u.update_activity_tracking(request.remote_addr)

                next_url = request.form.get('next')

                if next_url == url_for('user.login') or next_url == '' or next_url is None:
                    next_url = url_for('user.dashboard')

                if next_url:
                    return redirect(safe_next_url(next_url), code=307)

                if current_user.role == 'admin':
                    return redirect(url_for('admin.dashboard'))
            else:
                flash('This account has been disabled.', 'error')
        else:
            flash('Your username/email or password is incorrect.', 'error')

    else:
        if len(form.errors) > 0:
            print(form.errors)

    return render_template('user/login.html', form=form)


@user.route('/logout')
@login_required
def logout():
    logout_user()

    flash('You have been logged out.', 'success')
    return redirect(url_for('user.login'))


@user.route('/account/begin_password_reset', methods=['GET', 'POST'])
@anonymous_required()
def begin_password_reset():
    form = BeginPasswordResetForm()

    if form.validate_on_submit():
        u = User.initialize_password_reset(request.form.get('identity'))

        flash('An email has been sent to {0}.'.format(u.email), 'success')
        return redirect(url_for('user.login'))

    return render_template('user/begin_password_reset.html', form=form)


@user.route('/account/password_reset', methods=['GET', 'POST'])
@anonymous_required()
def password_reset():
    form = PasswordResetForm(reset_token=request.args.get('reset_token'))

    if form.validate_on_submit():
        u = User.deserialize_token(request.form.get('reset_token'))

        if u is None:
            flash('Your reset token has expired or was tampered with.',
                  'error')
            return redirect(url_for('user.begin_password_reset'))

        form.populate_obj(u)
        u.password = User.encrypt_password(request.form.get('password'))
        u.save()

        if login_user(u):
            flash('Your password has been reset.', 'success')
            return redirect(url_for('user.dashboard'))

    return render_template('user/password_reset.html', form=form)


@user.route('/signup', methods=['GET', 'POST'])
@anonymous_required()
@csrf.exempt
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        if db.session.query(exists().where(User.email == request.form.get('email'))).scalar():
            flash('There is already an account with this email. Please login.', 'error')
            return redirect(url_for('user.login'))

        if db.session.query(exists().where(func.lower(Domain.name) == request.form.get('domain').lower())).scalar():
            flash('That domain is already in use. Please try another.', 'error')
            return render_template('user/signup.html', form=form)

        u = User()

        form.populate_obj(u)
        u.password = User.encrypt_password(request.form.get('password'))
        u.role = 'creator'
        u.save()

        # Create the domain from the form
        from app.blueprints.api.api_functions import create_domain
        create_domain(u, form)

        if login_user(u):

            # from app.blueprints.user.tasks import send_welcome_email
            # from app.blueprints.contact.mailerlite import create_subscriber

            # send_welcome_email.delay(current_user.email)
            # create_subscriber(current_user.email)

            flash("You've successfully signed up!", 'success')
            return redirect(url_for('user.dashboard'))

    return render_template('user/signup.html', form=form)


# @user.route('/signup', methods=['GET', 'POST'])
# @anonymous_required()
# @csrf.exempt
# def signup():
#     from app.blueprints.api.api_functions import validate_signup, populate_signup, print_traceback
#
#     form = SignupForm(request.form)
#
#     try:
#         if request.method == 'POST':
#             print("posting")
#             if form.validate():
#                 print("form is valid")
#                 if db.session.query(exists().where(User.email == request.form.get('email'))).scalar():
#                     flash('There is already an account with this email. Please login.', 'error')
#                     return redirect(url_for('user.login'))
#
#                 u = User()
#
#                 populate_signup(request, u)
#                 u.password = User.encrypt_password(request.form.get('password'))
#                 u.save()
#
#                 if login_user(u):
#
#                     from app.blueprints.user.tasks import send_welcome_email
#                     from app.blueprints.contact.mailerlite import create_subscriber
#
#                     send_welcome_email.delay(current_user.email)
#                     create_subscriber(current_user.email)
#
#                     flash("You've successfully signed up!", 'success')
#                     return redirect(url_for('user.dashboard'))
#             print("form not valid")
#     except Exception as e:
#         print_traceback(e)
#
#     return render_template('user/signup.html', form=form)


@user.route('/welcome', methods=['GET', 'POST'])
@login_required
def welcome():
    if current_user.username:
        flash('You already picked a username.', 'warning')
        return redirect(url_for('user.dashboard'))

    form = WelcomeForm()

    if form.validate_on_submit():
        current_user.username = request.form.get('username')
        current_user.save()

        flash('Your username has been set.', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('user/welcome.html', form=form, payment=current_user.payment_id)


@user.route('/settings/update_credentials', methods=['GET', 'POST'])
@login_required
def update_credentials():
    form = UpdateCredentials(current_user, uid=current_user.id)

    if form.validate_on_submit():
        new_password = request.form.get('password', '')
        current_user.email = request.form.get('email')

        if new_password:
            current_user.password = User.encrypt_password(new_password)

        current_user.save()

        flash('Your sign in settings have been updated.', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('user/update_credentials.html', form=form)


# Dashboard -------------------------------------------------------------------
@user.route('/dashboard', methods=['GET','POST'])
@csrf.exempt
def root_dashboard():
    feedbacks = Feedback.query.all()
    statuses = Status.query.all()

    for f in feedbacks:
        f.votes = int(f.votes)

    feedbacks.sort(key=lambda x: x.created_on, reverse=True)
    return render_template('user/dashboard.html', current_user=current_user, feedbacks=feedbacks, statuses=statuses)


@user.route('/dashboard', subdomain='<subdomain>', methods=['GET','POST'])
@csrf.exempt
@cross_origin()
def dashboard(subdomain):
    if not subdomain or subdomain == '<invalid>':
        subdomain = 'demo'

    feedbacks = Feedback.query.filter(Feedback.domain == subdomain).all()
    statuses = Status.query.all()

    for f in feedbacks:
        f.votes = int(f.votes)

    feedbacks.sort(key=lambda x: x.created_on, reverse=True)
    return render_template('user/dashboard.html', current_user=current_user, feedbacks=feedbacks, statuses=statuses, subdomain=subdomain)


# Feedback -------------------------------------------------------------------
@user.route('/feedback', methods=['GET','POST'])
@login_required
@csrf.exempt
def feedback():
    feedback = Feedback.query.filter(Feedback.user_id == current_user.id).all()
    statuses = Status.query.all()

    for f in feedback:
        f.votes = int(f.votes)

    feedback.sort(key=lambda x: x.votes, reverse=True)

    return render_template('user/feedback.html', current_user=current_user, feedbacks=feedback, statuses=statuses)


@user.route('/dashboard/<sort>', subdomain='<subdomain>', methods=['GET','POST'])
@csrf.exempt
def sort(sort, subdomain):
    feedbacks = Feedback.query.filter(Feedback.domain == subdomain).all()
    statuses = Status.query.all()

    if sort == 'newest':
        feedbacks.sort(key=lambda x: x.created_on, reverse=True)
    elif sort == 'oldest':
        feedbacks.sort(key=lambda x: x.created_on)
    else:
        for f in feedbacks:
            f.votes = int(f.votes)

        feedbacks.sort(key=lambda x: x.votes, reverse=True)

    return render_template('user/dashboard.html', current_user=current_user, feedbacks=feedbacks, statuses=statuses, sort=sort)


@user.route('/feedback/<status>', subdomain='<subdomain>', methods=['GET','POST'])
@csrf.exempt
def filter(status, subdomain):
    feedbacks = Feedback.query.filter(and_(Feedback.domain == subdomain, Feedback.status == status)).all()
    statuses = Status.query.all()

    for f in feedbacks:
        f.votes = int(f.votes)

    feedbacks.sort(key=lambda x: x.votes, reverse=True)

    return render_template('user/feedback.html', current_user=current_user, feedbacks=feedbacks, statuses=statuses, filter=filter)


@user.route('/view/<feedback_id>', subdomain='<subdomain>', methods=['GET','POST'])
@csrf.exempt
def view_feedback(feedback_id, subdomain):
    f = Feedback.query.filter(Feedback.feedback_id == feedback_id).scalar()
    statuses = Status.query.all()
    return render_template('user/view_feedback.html', current_user=current_user, feedback=f, statuses=statuses, subdomain=subdomain)


# Votes -------------------------------------------------------------------
@user.route('/add_vote', methods=['GET','POST'])
@login_required
@csrf.exempt
def add_vote():
    if request.method == 'POST':
        if 'feedback_id' in request.form:
            feedback_id = request.form['feedback_id']
            from app.blueprints.api.api_functions import add_vote
            add_vote(feedback_id, current_user.id)

    return redirect(url_for('user.feedback'))


# Roadmap -------------------------------------------------------------------
@user.route('/roadmap', methods=['GET','POST'])
@login_required
@csrf.exempt
def roadmap():

    # if current_user.role == 'admin':
        # return redirect(url_for('admin.dashboard'))

    return render_template('user/roadmap.html', current_user=current_user)


# Settings -------------------------------------------------------------------
@user.route('/settings', methods=['GET','POST'])
@login_required
@csrf.exempt
def settings():

    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))

    c = Customer.query.filter(Customer.user_id == current_user.id).scalar()
    card = get_card(c)

    return render_template('user/settings.html', current_user=current_user, card=card)


# Actions -------------------------------------------------------------------
@user.route('/add_workspace', methods=['GET','POST'])
@login_required
@csrf.exempt
def add_workspace():
    if request.method == 'POST':
        try:
            title = request.form['title']
            domain = request.form['domain']
            description = request.form['description']

            from app.blueprints.api.api_functions import create_workspace
            w = create_workspace(current_user.id, title, domain, description)

            if w is not None:
                flash("Successfully created your workspace.", "success")
            else:
                flash("There was an error creating your workspace.", "error")

            return redirect(url_for('user.dashboard'))
        except Exception:
            flash("There was an error creating your workspace.", "error")
            return redirect(url_for('user.dashboard'))

    return render_template('user/add_workspace.html', current_user=current_user)


@user.route('/add_feedback', methods=['POST'])
@login_required
@csrf.exempt
def add_feedback():
    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            # email = request.form['email']

            from app.blueprints.api.api_functions import create_feedback
            f = create_feedback(current_user.id, None, title, description)

            return redirect(url_for('user.dashboard'))
        except Exception:
            flash("Uh oh, something went wrong!", "error")
            return redirect(url_for('user.dashboard'))

    return render_template('user/add_feedback.html', current_user=current_user)


# Demo -------------------------------------------------------------------
@user.route('/demo', methods=['GET','POST'])
@csrf.exempt
def demo():
    feedbacks = Feedback.query.filter(Feedback.user_id == 2).all()
    statuses = Status.query.all()

    for f in feedbacks:
        f.votes = int(f.votes)

    feedbacks.sort(key=lambda x: x.created_on, reverse=True)
    return render_template('user/dashboard.html', current_user=current_user, feedbacks=feedbacks, statuses=statuses)


@user.route('/demo_feedback', methods=['POST'])
@login_required
@csrf.exempt
def demo_feedback():
    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']

            from app.blueprints.api.api_functions import create_feedback
            f = create_feedback(2, None, title, description)

            return redirect(url_for('user.demo'))
        except Exception:
            flash("Uh oh, something went wrong!", "error")
            return redirect(url_for('user.demo'))

    return render_template('user/add_feedback.html', current_user=current_user)


# Contact us -------------------------------------------------------------------
@user.route('/contact', methods=['GET','POST'])
@csrf.exempt
def contact():
    if request.method == 'POST':
        from app.blueprints.user.tasks import send_contact_us_email
        send_contact_us_email.delay(request.form['email'], request.form['message'])

        flash('Thanks for your email! You can expect a response shortly.', 'success')
        return redirect(url_for('user.contact'))
    return render_template('user/contact.html', current_user=current_user)
