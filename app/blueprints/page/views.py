from flask import Blueprint, render_template, flash
from app.extensions import cache, timeout
from config import settings
from app.extensions import db, csrf
from flask import redirect, url_for, request, current_app
from flask_login import current_user, login_required
import requests
import ast
import json
import traceback
from sqlalchemy import and_, exists, text
from importlib import import_module
import os
import random

page = Blueprint('page', __name__, template_folder='templates')


@page.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))

    return render_template('page/index.html',
                           plans=settings.STRIPE_PLANS)


@page.route('/', subdomain="<domain>", methods=['GET','POST'])
@login_required
@csrf.exempt
def subdomain(domain):
    return redirect(url_for('user.dashboard'))


@page.route('/terms')
def terms():
    return render_template('page/terms.html')


@page.route('/privacy')
def privacy():
    return render_template('page/privacy.html')


@page.route('/index')
def index():
    return render_template('page/index.html', plans=settings.STRIPE_PLANS)
