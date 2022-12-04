from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db, login_manager
from models import User

main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@main.route('/')
def index():
    return render_template('index.html')

