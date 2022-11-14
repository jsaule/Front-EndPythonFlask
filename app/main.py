from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from forms import SignUpForm, LoginForm, NotesForm, TagsForm, SearchForm
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin, login_user, current_user, LoginManager, login_required, logout_user
from flask_migrate import Migrate
import json

# creates Flask instance
app = Flask(__name__)

# set configs
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "data.sqlite")
app.config['SECRET_KEY'] = 'SSDSDDSDSDSFSLGJNAOOAJGOAJNWARGAWRGAWRG'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# create database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# sets logging in
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

#-----------------------------------------------------------------------------------------------#
#------------------------------------------models-----------------------------------------------#
#-----------------------------------------------------------------------------------------------#

class Users(db.Model, UserMixin):
    '''A class to create user'''
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(70))
    name = db.Column(db.String(120), nullable=False)
    notes = db.relationship('Notes')

    def __repr__(self):
        name = self.name
        email = self.email
        return (name, email)

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.String(10000), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(100), unique=True)

    def __repr__(self):
        tag_name = self.tag_name
        return ("Tag id: {self.id}, title: {self.tag_name}>", tag_name)

#-----------------------------------------------------------------------------------------------#
# -----------------------------routes not requiring authentication------------------------------#
#-----------------------------------------------------------------------------------------------#

# about us page
@app.route('/aboutus')
def aboutus():
    form = SearchForm()
    return render_template("aboutus.html", user=current_user, form=form)

# invalid URL
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html", user=current_user), 404

# internal server error
@app.errorhandler(500)
def page_not_found(error):
    return render_template("500.html", user=current_user), 500

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

#-----------------------------------------------------------------------------------------------#
# -------------------------------routes requiring authentication--------------------------------#
#-----------------------------------------------------------------------------------------------#

@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    form = NotesForm()
    tags_form = TagsForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        new_note = Notes(title=title, body=body, user_id=current_user.id)
        db.session.add(new_note)
        db.session.commit()
        flash('Note added!', category='success')
        return redirect(url_for('home'))
    if tags_form.validate_on_submit():
        tag_name = tags_form.tag_name.data
        new_tag = Tags(tag_name=tag_name)
        db.session.add(new_tag)
        db.session.commit()
        flash('Tag added!', category='success')
        return redirect(url_for('home'))
    try:
        all_tags = Tags.query.all()
    except:
        all_tags = []
    return render_template("home.html", form=form, tags_form=tags_form, user=current_user, all_tags=all_tags)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out!", category="success")
    return redirect(url_for('login'))

@app.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Notes.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            flash('Note removed!', category='success')
    return jsonify({})

@app.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(id):
    form = NotesForm()
    to_update_note = Notes.query.get_or_404(id)
    if form.validate_on_submit():
        to_update_note.title = form.title.data
        to_update_note.body = form.body.data
        db.session.commit()
        flash('Note updated successfully!', category="success")
        return redirect(url_for('home'))
    form.body.data = to_update_note.body
    form.title.data = to_update_note.title
    return render_template("edit.html", form=form, user=current_user, note=to_update_note)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    notes = Notes.query
    if form.validate_on_submit():
        note_searched = form.searched.data
        notes = notes.filter(Notes.title.like('%' + note_searched + '%'))
        notes = notes.order_by(Notes.title).all()
        return render_template("search.html", form=form, searched=note_searched, user=current_user, notes=notes)

@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

@app.route('/notes/<int:id>')
@login_required
def note(id):
    note = Notes.query.get_or_404(id)
    return render_template('note.html', note=note, user=current_user)