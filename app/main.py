from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from forms import SignUpForm, LoginForm
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin, login_user, current_user, LoginManager, login_required, logout_user

# creates Flask instance
app = Flask(__name__)

# set configs
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "data.sqlite")
app.config['SECRET_KEY'] = 'SSDSDDSDSDSFSLGJNAOOAJGOAJNWARGAWRGAWRG'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# create database
db = SQLAlchemy(app)

# sets logging in
login_manager = LoginManager()
login_manager.login_view = 'app.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

# --------------------------------models------------------------------------------------------------

class Users(db.Model, UserMixin):
    '''A class to create user'''
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(70))
    name = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        name = self.name
        email = self.email
        return (name, email)

# --------------------------------routes not requiring authentication--------------------------------------

# about us page
@app.route('/aboutus')
def aboutus():
    return render_template("aboutus.html")

# invalid URL
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

# internal server error
@app.errorhandler(500)
def page_not_found(error):
    return render_template("500.html"), 500

# allows user to sign up
@app.route('/sign-up', methods=['GET', 'POST']) #add lower
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        user = Users.query.filter_by(email=email.lower()).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Your email must be longer than 3 characters.', category="error")
        elif len(name) <2:
            flash('Your name must be longer than 1 character.', category="error")
        elif password != confirm_password:
            flash('Your passwords don\'t match.', category="error")
        elif len(password) < 7:
            flash('Your password must be longer than 6 characters.', category="error")
        else:
            new_user = Users(email=email, name=name, password=generate_password_hash(password, method='sha256'))
            flash('Account created successfully!', category="success")
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for('home'))
    form.email.data = ''
    form.name.data = ''
    form.password.data = '' 
    return render_template("sign_up.html", user=current_user, form=form)

# allows user to log in
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = Users.query.filter_by(email=email.lower()).first()
        if user is not None:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for('home'))
            else: 
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist', category="error")
    form.email.data = ''
    form.password.data = ''
    return render_template("login.html", user=current_user, form=form)

# -------------------------------routes requiring authentication--------------------------------------

@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template('home.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out!", category="success")
    return redirect(url_for('login'))