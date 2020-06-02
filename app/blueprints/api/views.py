from flask import Blueprint, render_template, json, flash
from app.extensions import csrf

api = Blueprint('api', __name__, template_folder='templates')


@api.route('/test', methods=['GET','POST'])
@csrf.exempt
def test():
    return