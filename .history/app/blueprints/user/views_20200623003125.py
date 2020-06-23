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
import requests
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
from app.blueprints.base.models.feedback import Feedback
from app.blueprints.base.models.status import Status
from app.blueprints.base.models.vote import Vote
from app.blueprints.base.functions import print_traceback

user = Blueprint('user', __name__, template_folder='templates')
use_username = False


# Login and Credentials -------------------------------------------------------------------
@user.route('/login', methods=['GET', 'POST'])
@user.route('/login', subdomain='<subdomain>', methods=['GET', 'POST'])
@anonymous_required()
@csrf.exempt
def login(subdomain=None):

    if subdomain:
        form = LoginForm(next=request.args.get('next'))

        if form.validate_on_submit():

            u = User.find_by_identity(request.form.get('identity'))

            if u and u.is_active() and u.authenticated(password=request.form.get('password')):
                if login_user(u, remember=True) and u.is_active():

                    if current_user.role == 'admin':
                        return redirect(url_for('admin.dashboard'))

                    u.update_activity_tracking(request.remote_addr)

                    next_url = request.form.get('next')

                    if next_url == url_for('user.login', subdomain=subdomain) or next_url == '' or next_url is None:
                        next_url = url_for('user.dashboard', subdomain=subdomain)

                    if next_url:
                        return redirect(safe_next_url(next_url), code=307)

                else:
                    flash('This account has been disabled.', 'error')
            else:
                flash('Your username/email or password is incorrect.', 'error')

        else:
            if len(form.errors) > 0:
                print(form.errors)

        return render_template('user/login.html', subdomain=subdomain, form=form)
    else:
        form = LoginFormAnon(next=request.args.get('next'))

        if form.validate_on_submit():
            u = User.find_by_identity(request.form.get('identity'))

            if u and u.is_active() and u.authenticated(password=request.form.get('password')):
                # If the user doesn't have a company, make them sign up for one
                subdomain = request.form.get('domain')

                if not db.session.query(exists().where(func.lower(Domain.name) == subdomain.lower())).scalar():
                    flash(Markup("That domain wasn't found. Please try again or <a href='" + url_for('user.signup') + "'><span class='text-indigo-700'><u>create a new company</span></u></a>."),
                          category='error')
                    return render_template('user/login.html', form=form)

                if login_user(u, remember=True) and u.is_active():
                    if current_user.role == 'admin':
                        return redirect(url_for('admin.dashboard'))

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


'''
Signup to post feedback in an existing domain
'''


@user.route('/signup', methods=['GET', 'POST'])
@user.route('/signup', subdomain='<subdomain>', methods=['GET', 'POST'])
@anonymous_required()
@csrf.exempt
def signup(subdomain=None):
    if subdomain:
        form = SignupForm()

        try:
            if form.validate_on_submit():
                if db.session.query(exists().where(User.email == request.form.get('email'))).scalar():
                    flash('There is already an account with this email. Please login.', 'error')
                    return redirect(url_for('user.login', subdomain=subdomain))

                subdomain = request.form.get('domain').replace(' ', '')

                u = User()

                form.populate_obj(u)
                u.password = User.encrypt_password(request.form.get('password'))
                u.role = 'member'
                u.save()

                if login_user(u):
                    # from app.blueprints.user.tasks import send_welcome_email
                    # from app.blueprints.contact.mailerlite import create_subscriber

                    # send_welcome_email.delay(current_user.email)
                    # create_subscriber(current_user.email)

                    # Create the domain from the form
                    # from app.blueprints.base.api_functions import create_domain
                    # create_domain(u, form)

                    flash("You've successfully signed up!", 'success')
                    return redirect(url_for('user.dashboard', subdomain=subdomain))
        except Exception as e:
            print_traceback(e)

        return render_template('user/signup.html', subdomain=subdomain, form=form)
    else:
        form = SignupFormAnon()

        try:
            if form.validate_on_submit():
                if db.session.query(exists().where(User.email == request.form.get('email'))).scalar():
                    flash('There is already an account with this email. Please login.', 'error')

                    u = User.query.filter(User.email == request.form.get('email')).scalar()
                    if u.domain is not None:
                        return redirect(url_for('user.login', subdomain=u.domain))
                    return redirect(url_for('user.login'))

                subdomain = request.form.get('domain').replace(' ', '')

                if db.session.query(exists().where(func.lower(Domain.name) == subdomain.lower())).scalar():
                    flash('That domain is already in use. Please try another.', 'error')
                    return render_template('user/signup.html', subdomain=subdomain, form=form)

                u = User()

                form.populate_obj(u)
                u.password = User.encrypt_password(request.form.get('password'))
                u.role = 'creator'
                
                # Save the user to the database
                u.save()

                if login_user(u):
                    # from app.blueprints.user.tasks import send_welcome_email
                    # from app.blueprints.contact.mailerlite import create_subscriber

                    # send_welcome_email.delay(current_user.email)
                    # create_subscriber(current_user.email)

                    # Create the domain from the form
                    from app.blueprints.base.functions import create_domain
                    if create_domain(u, form):

                        flash("You've successfully signed up!", 'success')
                        return redirect(url_for('user.start', subdomain=subdomain))
                    else:
                        flash("There was an error creating this domain. Please try again.", 'error')
                        return redirect(url_for('user.signup', form=form))
        except Exception as e:
            print_traceback(e)

        return render_template('user/signup.html', form=form)


@user.route('/logout')
@user.route('/logout', subdomain='<subdomain>')
@login_required
def logout(subdomain=None):
    if subdomain:
        logout_user()
        flash('You have been logged out.', 'success')
        return redirect(url_for('user.dashboard', subdomain=subdomain))
    else:
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
            return redirect(url_for('user.settings'))

    return render_template('user/password_reset.html', form=form)


@user.route('/welcome', subdomain='<subdomain>', methods=['GET', 'POST'])
@login_required
def welcome(subdomain=None):
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


@user.route('/start', methods=['GET', 'POST'])
@user.route('/start/<subdomain>', methods=['GET', 'POST'])
@login_required
def start(subdomain=None):
    if not (current_user.is_authenticated and current_user.domain == subdomain):
        return redirect(url_for('user.login'))

    domain = Domain.query.filter(Domain.name == current_user.domain).scalar()

    return render_template('user/start.html', current_user=current_user, domain=domain, subdomain=subdomain)


@user.route('/settings/update_credentials', methods=['GET', 'POST'])
@user.route('/settings/update_credentials', subdomain='<subdomain>', methods=['GET', 'POST'])
@login_required
def update_credentials(subdomain=None):
    form = UpdateCredentials(current_user, uid=current_user.id)

    if form.validate_on_submit():
        username = request.form.get('username', '')
        new_password = request.form.get('password', '')
        current_user.email = request.form.get('email')

        if new_password:
            current_user.password = User.encrypt_password(new_password)

        current_user.username = username
        current_user.save()

        flash('Your credentials have been updated.', 'success')
        return redirect(url_for('user.settings', subdomain=subdomain))

    return render_template('user/update_credentials.html', form=form, subdomain=subdomain)


@user.route('/dashboard', methods=['GET','POST'])
@user.route('/dashboard', subdomain='<subdomain>', methods=['GET','POST'])
@csrf.exempt
@cross_origin()
def dashboard(subdomain=None):
    # if not subdomain or subdomain == '<invalid>':
    #     subdomain = 'demo'

    if subdomain:
        d = Domain.query.filter(Domain.name == subdomain).scalar()
        feedbacks = Feedback.query.filter(Feedback.domain_id == d.domain_id).all()

        if current_user.is_authenticated:
            votes = Vote.query.filter(and_(Vote.user_id == current_user.id, Vote.domain_id == d.domain_id)).all()
        else:
            votes = None

        statuses = Status.query.all()

        for f in feedbacks:
            f.votes = int(f.votes)

        feedbacks.sort(key=lambda x: x.created_on, reverse=True)
        return render_template('user/dashboard.html', current_user=current_user, feedbacks=feedbacks, statuses=statuses, domain=d, subdomain=subdomain, votes=votes, use_username=use_username)
    else:
        d = Domain.query.filter(Domain.name == 'demo').scalar()
        feedbacks = Feedback.query.all()
        statuses = Status.query.all()

        for f in feedbacks:
            f.votes = int(f.votes)

        feedbacks.sort(key=lambda x: x.created_on, reverse=True)
        return render_template('user/dashboard.html', current_user=current_user, feedbacks=feedbacks, statuses=statuses, domain=d, subdomain='demo', use_username=use_username)


@user.route('/dashboard', methods=['GET','POST'])
@csrf.exempt
@cross_origin()
def demo():
    return redirect(url_for('user.dashboard', subdomain='demo'))


# Feedback -------------------------------------------------------------------
'''
View feedback details
'''


@user.route('/feedback/<feedback_id>', methods=['GET','POST'])
@user.route('/feedback/<feedback_id>', subdomain='<subdomain>', methods=['GET','POST'])
@csrf.exempt
def feedback(feedback_id, subdomain):
    f = Feedback.query.filter(Feedback.feedback_id == feedback_id).scalar()
    voted = db.session.query(exists().where(and_(Vote.feedback_id == feedback_id, Vote.user_id == current_user.id))).scalar()
    statuses = Status.query.all()
    return render_template('user/view_feedback.html', current_user=current_user, feedback=f, statuses=statuses, subdomain=subdomain, voted=voted, use_username=use_username)


'''
Add feedback to the list
'''


@user.route('/add_feedback', methods=['POST'])
@user.route('/add_feedback', subdomain='<subdomain>', methods=['POST'])
@csrf.exempt
def add_feedback(subdomain=None):
    if subdomain:
        # If there is no user, redirect them to the login for this domain
        # if not current_user.is_authenticated:
            # return redirect(url_for('user.login', subdomain=subdomain))

        if request.method == 'POST':
            try:
                title = request.form['title']
                description = request.form['description']
                email = request.form['email'] if 'email' in request.form else ''

                from app.blueprints.base.functions import create_feedback

                if current_user.is_authenticated:
                    create_feedback(current_user, subdomain, None, title, description)
                else:
                    create_feedback(None, subdomain, email, title, description)

                return redirect(url_for('user.dashboard', subdomain=subdomain))
            except Exception:
                flash("Uh oh, something went wrong!", "error")
                return redirect(url_for('user.dashboard', subdomain=subdomain))

        return render_template('user/add_feedback.html', current_user=current_user, subdomain=subdomain)
    else:
        if request.method == 'POST':
            try:
                title = request.form['title']
                description = request.form['description']
                email = request.form['email'] if 'email' in request.form else None

                from app.blueprints.base.functions import create_feedback

                if current_user.is_authenticated:
                    create_feedback(current_user, 'demo', None, title, description)
                else:
                    create_feedback(None, 'demo', email, title, description)

                return redirect(url_for('user.dashboard'))
            except Exception:
                flash("Uh oh, something went wrong!", "error")
                return redirect(url_for('user.dashboard'))

        return render_template('user/add_feedback.html', current_user=current_user)


'''
Update the feedback
'''


@user.route('/update_feedback', subdomain='<subdomain>', methods=['POST'])
@csrf.exempt
def update_feedback(subdomain=None):
    if request.method == 'POST':
        try:
            feedback_id = request.form['feedback_id']
            title = request.form['title']
            description = request.form['description']
            status_id = request.form['status']

            from app.blueprints.base.functions import update_feedback
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


@user.route('/dashboard/<s>', methods=['GET', 'POST'])
@user.route('/dashboard/<s>', subdomain='<subdomain>', methods=['GET','POST'])
@csrf.exempt
def sort_feedback(s, subdomain=None):
    if subdomain:
        feedbacks = Feedback.query.filter(Feedback.domain == subdomain).all()
        statuses = Status.query.all()

        if s == 'newest':
            feedbacks.sort(key=lambda x: x.created_on, reverse=True)
        elif s == 'oldest':
            feedbacks.sort(key=lambda x: x.created_on)
        else:
            for f in feedbacks:
                f.votes = int(f.votes)

            feedbacks.sort(key=lambda x: x.votes, reverse=True)

        return render_template('user/dashboard.html', current_user=current_user, feedbacks=feedbacks, statuses=statuses, s=s, subdomain=subdomain)
    else:
        feedbacks = Feedback.query.filter(Feedback.domain == 'demo').all()
        statuses = Status.query.all()

        if s == 'newest':
            feedbacks.sort(key=lambda x: x.created_on, reverse=True)
        elif s == 'oldest':
            feedbacks.sort(key=lambda x: x.created_on)
        else:
            for f in feedbacks:
                f.votes = int(f.votes)

            feedbacks.sort(key=lambda x: x.votes, reverse=True)

        return render_template('user/dashboard.html', current_user=current_user, feedbacks=feedbacks, statuses=statuses, s=s, subdomain=demo)


# Votes -------------------------------------------------------------------
'''
Add or remove a vote
'''


@user.route('/update_vote', subdomain='<subdomain>', methods=['GET','POST'])
@csrf.exempt
def update_vote(subdomain=None):
    if request.method == 'POST':
        if 'feedback_id' in request.form and 'user_id' in request.form:
            feedback_id = request.form['feedback_id']
            user_id = request.form['user_id']
            from app.blueprints.base.functions import add_vote, remove_vote

            if db.session.query(exists().where(and_(Vote.feedback_id == feedback_id, Vote.user_id == user_id))).scalar():
                vote = Vote.query.filter(and_(Vote.feedback_id == feedback_id, Vote.user_id == user_id)).scalar()
                remove_vote(feedback_id, vote)
            else:
                add_vote(feedback_id, user_id)

            return jsonify({'success': 'Success'})

    return redirect(url_for('user.dashboard', subdomain=subdomain))


# Roadmap -------------------------------------------------------------------
@user.route('/roadmap', methods=['GET','POST'])
@user.route('/roadmap', subdomain='<subdomain>', methods=['GET','POST'])
@csrf.exempt
def roadmap(subdomain=None):
    return render_template('user/roadmap.html', current_user=current_user, subdomain=subdomain)


# Settings -------------------------------------------------------------------
@user.route('/settings', methods=['GET','POST'])
@user.route('/settings', subdomain='<subdomain>', methods=['GET','POST'])
@login_required
@csrf.exempt
def settings(subdomain=None):
    if subdomain:
        domain = Domain.query.filter(Domain.user_id == current_user.id).scalar()
        return render_template('user/settings.html', current_user=current_user, domain=domain, subdomain=subdomain)
    else:
        return render_template('user/settings.html', current_user=current_user)


# Actions -------------------------------------------------------------------
@user.route('/send_invite', subdomain='<subdomain>', methods=['GET','POST'])
@login_required
@csrf.exempt
def send_invite(subdomain=None):
    return redirect(url_for('user.dashboard', subdomain=subdomain))


@user.route('/check_domain_status', methods=['GET','POST'])
@login_required
@csrf.exempt
@cross_origin()
def check_domain_status():
    try:
        if request.method == 'POST':
            if 'subdomain' in request.form and 'user_id' in request.form:
                subdomain = request.form['subdomain']
                user_id = request.form['user_id']

                u = User.query.filter(User.id == user_id).scalar()

                if subdomain == u.domain:
                    r = requests.get('https://' + subdomain + '.getwishlist.io')
                    if r.status_code == 200:
                        return jsonify({'success': 'Success'})
        return jsonify({'error': 'Error'})
    except Exception as e:
        return jsonify({'error': 'Error'})


@user.route('/set_domain_privacy', methods=['POST'])
@csrf.exempt
def set_domain_privacy():
    try:
        if request.method == 'POST':
            if 'domain_id' in request.form:
                domain_id = request.form['domain_id']

                d = Domain.query.filter(Domain.domain_id == domain_id).scalar()
                d.is_private = True
                d.save()

                return jsonify({'success': 'Success'})
        return jsonify({'error': 'Error'})
    except Exception as e:
        return jsonify({'error': 'Error'})


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
