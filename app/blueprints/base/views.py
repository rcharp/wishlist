from flask import Blueprint, render_template, json, flash, request, redirect, url_for
from app.extensions import csrf
from app.blueprints.base.test import test as t
from app.blueprints.base.functions import print_traceback

base = Blueprint('base', __name__, template_folder='templates')


@base.route('/test', methods=['GET', 'POST'])
@csrf.exempt
def test():
    if request.method == 'POST':
        domain = request.form['domain']

        try:
            results = t()
            # print(results)
            flash("Test was successful.", 'success')
            flash("Results are: " + str(results), 'danger')
            return redirect(url_for('user.dashboard'))
        except Exception as e:
            print_traceback(e)
            flash("Test was unsuccessful.", 'error')
            return redirect(url_for('user.dashboard'))
    else:
        flash("Test wasn't run.", 'error')
        return redirect(url_for('user.dashboard'))