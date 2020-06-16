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
    LoginFormAnon,
    BeginPasswordResetForm,
    PasswordResetForm,
    SignupForm,
    SignupFormAnon,
    WelcomeForm,
    UpdateCredentials)

from app.extensions import cache, csrf, timeout, db
from importlib import import_module
from sqlalchemy import or_, and_, exists, inspect, func
from app.blueprints.api.models.feedback import Feedback
from app.blueprints.api.models.status import Status
from app.blueprints.api.models.vote import Vote

user = Blueprint('user', __name__, template_folder='templates')


# Login and Credentials -------------------------------------------------------------------
@user.route('/login', subdomain='<subdomain>', methods=['GET', 'POST'])
@anonymous_required()
@csrf.exempt
def login(subdomain):

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

                if next_url == url_for('user.login', subdomain=subdomain) or next_url == '' or next_url is None:
                    next_url = url_for('user.dashboard', subdomain=subdomain)

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

    return render_template('user/login.html', subdomain=subdomain, form=form)


@user.route('/login', methods=['GET', 'POST'])
@anonymous_required()
@csrf.exempt
def login_anon():

    form = LoginFormAnon(next=request.args.get('next'))

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

            # If the user doesn't have a company, make them sign up for one
            subdomain = request.form.get('domain')

            if not db.session.query(exists().where(func.lower(Domain.name) == subdomain.lower())).scalar():
                flash(Markup("That domain wasn't found. Please try again or <a href='" + url_for('user.signup_anon') + "'><span class='text-indigo-700'><u>create a new company</span></u></a>."),
                      category='error')
                return render_template('user/login.html', form=form)

            if login_user(u, remember=True) and u.is_active():
                u.update_activity_tracking(request.remote_addr)

                next_url = request.form.get('next')

                if next_url == url_for('user.login', subdomain=subdomain) or next_url == '' or next_url is None:
                    next_url = url_for('user.dashboard', subdomain=u.domain)

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


@user.route('/signup', subdomain='<subdomain>', methods=['GET', 'POST'])
@anonymous_required()
@csrf.exempt
def signup(subdomain):
    form = SignupForm()

    if form.validate_on_submit():
        if db.session.query(exists().where(User.email == request.form.get('email'))).scalar():
            flash('There is already an account with this email. Please login.', 'error')
            return redirect(url_for('user.login', subdomain=subdomain))

        subdomain = request.form.get('domain').replace(' ', '')

        # if db.session.query(exists().where(func.lower(Domain.name) == subdomain.lower())).scalar():
        #     flash('That domain is already in use. Please try another.', 'error')
        #     return render_template('user/signup.html', subdomain=subdomain, form=form)

        u = User()

        form.populate_obj(u)
        u.password = User.encrypt_password(request.form.get('password'))
        u.role = 'creator'
        u.save()

        if login_user(u):
            # from app.blueprints.user.tasks import send_welcome_email
            # from app.blueprints.contact.mailerlite import create_subscriber

            # send_welcome_email.delay(current_user.email)
            # create_subscriber(current_user.email)

            # Create the domain from the form
            # from app.blueprints.api.api_functions import create_domain
            # create_domain(u, form)

            flash("You've successfully signed up!", 'success')
            return redirect(url_for('user.dashboard', subdomain=subdomain))

    return render_template('user/signup.html', subdomain=subdomain, form=form)


@user.route('/signup', methods=['GET', 'POST'])
@anonymous_required()
@csrf.exempt
def signup_anon():
    form = SignupFormAnon()

    if form.validate_on_submit():
        if db.session.query(exists().where(User.email == request.form.get('email'))).scalar():
            flash('There is already an account with this email. Please login.', 'error')

            u = User.query.filter(User.email == request.form.get('email')).scalar()
            if u.domain is not None:
                return redirect(url_for('user.login', subdomain=u.domain))
            return redirect(url_for('user.login_anon'))

        subdomain = request.form.get('domain').replace(' ', '')

        if db.session.query(exists().where(func.lower(Domain.name) == subdomain.lower())).scalar():
            flash('That domain is already in use. Please try another.', 'error')
            return render_template('user/signup.html', subdomain=subdomain, form=form)

        u = User()

        form.populate_obj(u)
        u.password = User.encrypt_password(request.form.get('password'))
        u.role = 'creator'
        u.save()

        if login_user(u):
            # from app.blueprints.user.tasks import send_welcome_email
            # from app.blueprints.contact.mailerlite import create_subscriber

            # send_welcome_email.delay(current_user.email)
            # create_subscriber(current_user.email)

            # Create the domain from the form
            from app.blueprints.api.api_functions import create_domain
            if create_domain(u, form):
                flash("You've successfully signed up!", 'success')
                return redirect(url_for('user.settings_anon'))
            else:
                flash("There was an error creating this domain. Please try again.", 'error')
                return redirect(url_for('user.signup_anon'))

    return render_template('user/signup.html', form=form)


@user.route('/logout', subdomain='<subdomain>')
@login_required
def logout(subdomain):
    logout_user()

    flash('You have been logged out.', 'success')
    return redirect(url_for('user.login', subdomain=subdomain))


@user.route('/logout')
@login_required
def logout_anon():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('user.login_anon'))


@user.route('/account/begin_password_reset', subdomain='<subdomain>', methods=['GET', 'POST'])
@anonymous_required()
def begin_password_reset(subdomain):
    form = BeginPasswordResetForm()

    if form.validate_on_submit():
        u = User.initialize_password_reset(request.form.get('identity'))

        flash('An email has been sent to {0}.'.format(u.email), 'success')
        return redirect(url_for('user.login', subdomain=subdomain))

    return render_template('user/begin_password_reset.html', form=form)


@user.route('/account/password_reset', subdomain='<subdomain>', methods=['GET', 'POST'])
@anonymous_required()
def password_reset(subdomain):
    form = PasswordResetForm(reset_token=request.args.get('reset_token'))

    if form.validate_on_submit():
        u = User.deserialize_token(request.form.get('reset_token'))

        if u is None:
            flash('Your reset token has expired or was tampered with.',
                  'error')
            return redirect(url_for('user.begin_password_reset', subdomain=subdomain))

        form.populate_obj(u)
        u.password = User.encrypt_password(request.form.get('password'))
        u.save()

        if login_user(u):
            flash('Your password has been reset.', 'success')
            return redirect(url_for('user.dashboard', subdomain=subdomain))

    return render_template('user/password_reset.html', subdomain=subdomain, form=form)


@user.route('/welcome', subdomain='<subdomain>', methods=['GET', 'POST'])
@login_required
def welcome(subdomain):
    if current_user.username:
        flash('You already picked a username.', 'warning')
        return redirect(url_for('user.dashboard', subdomain=subdomain))

    form = WelcomeForm()

    if form.validate_on_submit():
        current_user.username = request.form.get('username')
        current_user.save()

        flash('Your username has been set.', 'success')
        return redirect(url_for('user.dashboard', subdomain=subdomain))

    return render_template('user/welcome.html', form=form, subdomain=subdomain)
    # return render_template('user/welcome.html', form=form, payment=current_user.payment_id, subdomain=subdomain)


@user.route('/welcome', methods=['GET', 'POST'])
@login_required
def welcome_anon():
    return redirect(url_for('user.login_anon'))


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
def dashboard_anon():
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

    d = Domain.query.filter(Domain.name == subdomain).scalar()
    feedbacks = Feedback.query.filter(Feedback.domain_id == d.domain_id).all()
    votes = Vote.query.filter(and_(Vote.user_id == current_user.id, Vote.domain_id == d.domain_id)).all()
    statuses = Status.query.all()

    for f in feedbacks:
        f.votes = int(f.votes)

    feedbacks.sort(key=lambda x: x.created_on, reverse=True)
    return render_template('user/dashboard.html', current_user=current_user, feedbacks=feedbacks, statuses=statuses, subdomain=subdomain, votes=votes)


@user.route('/dashboard', methods=['GET','POST'])
@csrf.exempt
@cross_origin()
def demo():
    return redirect(url_for('user.dashboard', subdomain='demo'))


# Feedback -------------------------------------------------------------------
'''
View feedback details
'''
@user.route('/feedback/<feedback_id>', subdomain='<subdomain>', methods=['GET','POST'])
@csrf.exempt
def feedback(feedback_id, subdomain):
    f = Feedback.query.filter(Feedback.feedback_id == feedback_id).scalar()
    voted = db.session.query(exists().where(and_(Vote.feedback_id == feedback_id, Vote.user_id == current_user.id))).scalar()
    statuses = Status.query.all()
    return render_template('user/view_feedback.html', current_user=current_user, feedback=f, statuses=statuses, subdomain=subdomain, voted=voted)


@user.route('/feedback/<feedback_id>', methods=['GET','POST'])
@csrf.exempt
def feedback_anon(feedback_id):
    f = Feedback.query.filter(Feedback.feedback_id == feedback_id).scalar()
    statuses = Status.query.all()
    return render_template('user/view_feedback.html', current_user=current_user, feedback=f, statuses=statuses, voted=False)


'''
Add feedback to the list
'''
@user.route('/add_feedback', subdomain='<subdomain>', methods=['POST'])
# @login_required
@csrf.exempt
def add_feedback(subdomain):

    # If there is no user, redirect them to the login for this domain
    if not current_user.is_authenticated:
        return redirect(url_for('user.login', subdomain=subdomain))

    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']

            from app.blueprints.api.api_functions import create_feedback
            create_feedback(current_user, subdomain, title, description)

            return redirect(url_for('user.dashboard', subdomain=subdomain))
        except Exception:
            flash("Uh oh, something went wrong!", "error")
            return redirect(url_for('user.dashboard', subdomain=subdomain))

    return render_template('user/add_feedback.html', current_user=current_user, subdomain=subdomain)


'''
Adding feedback to the demo
'''
@user.route('/add_feedback', methods=['POST'])
@login_required
@csrf.exempt
def add_feedback_anon():
    return redirect(url_for('user.signup_anon'))


'''
Update the feedback
'''
@user.route('/update_feedback', subdomain='<subdomain>', methods=['POST'])
@login_required
@csrf.exempt
def update_feedback(subdomain):
    if request.method == 'POST':
        try:
            feedback_id = request.form['feedback_id']
            title = request.form['title']
            description = request.form['description']
            status_id = request.form['status']

            from app.blueprints.api.api_functions import update_feedback
            if update_feedback(feedback_id, subdomain, title, description, status_id) is not None:
                return redirect(url_for('user.feedback', feedback_id=feedback_id, subdomain=subdomain))

            flash("Uh oh, something went wrong!", "error")
            return redirect(url_for('user.dashboard', subdomain=subdomain))
        except Exception:
            flash("Uh oh, something went wrong!", "error")
            return redirect(url_for('user.dashboard', subdomain=subdomain))

    return render_template('user/add_feedback.html', current_user=current_user, subdomain=subdomain)


'''
Sort the feedback by newest, oldest, or most votes
'''
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

    return render_template('user/dashboard.html', current_user=current_user, feedbacks=feedbacks, statuses=statuses, sort=sort, subdomain=subdomain)


'''
Filter feedback by status
'''
@user.route('/feedback/<status>', subdomain='<subdomain>', methods=['GET','POST'])
@csrf.exempt
def filter(status, subdomain):
    feedbacks = Feedback.query.filter(and_(Feedback.domain == subdomain, Feedback.status == status)).all()
    statuses = Status.query.all()

    for f in feedbacks:
        f.votes = int(f.votes)

    feedbacks.sort(key=lambda x: x.votes, reverse=True)

    return render_template('user/dashboard.html', current_user=current_user, feedbacks=feedbacks, statuses=statuses, filter=filter, subdomain=subdomain)


# Votes -------------------------------------------------------------------
'''
Add or remove a vote
'''
@user.route('/update_vote', subdomain='<subdomain>', methods=['GET','POST'])
@login_required
@csrf.exempt
def update_vote(subdomain):
    if request.method == 'POST':
        if 'feedback_id' in request.form and 'user_id' in request.form:
            feedback_id = request.form['feedback_id']
            user_id = request.form['user_id']
            from app.blueprints.api.api_functions import add_vote, remove_vote

            if db.session.query(exists().where(and_(Vote.feedback_id == feedback_id, Vote.user_id == user_id))).scalar():
                vote = Vote.query.filter(and_(Vote.feedback_id == feedback_id, Vote.user_id == user_id)).scalar()
                remove_vote(feedback_id, vote)
            else:
                add_vote(feedback_id, user_id)

            return jsonify({'success': 'Success'})

    return redirect(url_for('user.dashboard', subdomain=subdomain))


# Roadmap -------------------------------------------------------------------
@user.route('/roadmap', subdomain='<subdomain>', methods=['GET','POST'])
@login_required
@csrf.exempt
def roadmap(subdomain):
    return render_template('user/roadmap.html', current_user=current_user, subdomain=subdomain)


# Settings -------------------------------------------------------------------
@user.route('/settings', subdomain='<subdomain>', methods=['GET','POST'])
@login_required
@csrf.exempt
def settings(subdomain):
    domain = Domain.query.filter(Domain.user_id == current_user.id).scalar()
    return render_template('user/settings.html', current_user=current_user, domain=domain, subdomain=subdomain)


@user.route('/settings', methods=['GET','POST'])
@login_required
@csrf.exempt
def settings_anon():
    return render_template('user/settings.html', current_user=current_user)


# Actions -------------------------------------------------------------------
@user.route('/send_invite', subdomain='<subdomain>', methods=['GET','POST'])
@login_required
@csrf.exempt
def send_invite(subdomain):
    return redirect(url_for('user.dashboard', subdomain=subdomain))


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
