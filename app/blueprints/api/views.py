from flask import Blueprint, render_template, json, flash, request, redirect, url_for
from app.extensions import csrf

api = Blueprint('api', __name__, template_folder='templates')
