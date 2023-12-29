from flask import Flask
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__, template_folder="../app/templates/")

app.config['SECRET_KEY'] = 'your_secret_key'  # Замените 'your_secret_key' на случайную строку

login_manager = LoginManager(app)
