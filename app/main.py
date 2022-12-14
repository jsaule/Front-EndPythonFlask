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

# sets configs
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "data.sqlite")
app.config['SECRET_KEY'] = 'SSDSDDSDSDSFSLGJNAOOAJGOAJNWARGAWRGAWRG'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# creates database
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
        id = self.id
        name = self.name
        email = self.email
        return f"User id: {id}, name: {name}, email: {email}"

'''Association table between Notes and Tags'''
notes_tags = db.Table('notes_tags',
                    db.Column('notes_id', db.Integer, db.ForeignKey('notes.id')),
                    db.Column('tags_id', db.Integer, db.ForeignKey('tags.id'))
                    )

class Tags(db.Model):
    '''A class to create tag'''
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(100))

    def __repr__(self):
        id = self.id
        tag_name= self.tag_name
        return f"Tag id: {id}, title: {tag_name}"

class Notes(db.Model):
    '''A class to create Note'''
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.String(10000), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    note_tags = db.relationship('Tags', secondary=notes_tags, backref='tag_notes')

    def __repr__(self):
        id = self.id
        title = self.title
        tag_ids = [tag.id for tag in self.note_tags]
        return f"Note id: {id}, title: {title}, tag ids: {tag_ids}"

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

# main landing page
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    form = NotesForm()
    tags_form = TagsForm()
    form.tags.choices=[]
    for t in Tags.query.all():
        form.tags.choices.append((t.id, t.tag_name))
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        tags = [Tags.query.get(tag_id) for tag_id in form.tags.data]
        try:
            tags_dict = {}
            tags_o = form.tags.choices.append((t.id, t.tag_name))
            tags_dict_full = tags_dict.update(tags_o)
            for tg in tags_dict_full():
                selected_tag = Tags.query.get(tg)
                db.session.add(selected_tag)
        except:
            selected_tag = None
        new_note = Notes(title=title, body=body, note_tags=tags, user_id=current_user.id)
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
    notes = Notes.query.all()
    return render_template("home.html", form=form, tags_form=tags_form, user=current_user, all_tags=all_tags, notes=notes)

# allows user to logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out!", category="success")
    return redirect(url_for('login'))

# allows user to delete note
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

# allows user to delete tag
@app.route('/delete-tag', methods=['POST'])
@login_required
def delete_tag():
    tag = json.loads(request.data)
    tagId = tag['tagId']
    tag = Tags.query.get(tagId)
    if tag:
        db.session.delete(tag)
        db.session.commit()
        flash('Tag removed!', category='success')
    return jsonify({})

# allows user to edit note
@app.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(id):
    form = NotesForm()
    to_update_note = Notes.query.get_or_404(id)
    form.tags.choices=[]
    for t in Tags.query.all():
        form.tags.choices.append((t.id, t.tag_name))
    if form.validate_on_submit():
        to_update_note.title = form.title.data
        to_update_note.body = form.body.data
        to_update_note.note_tags = [Tags.query.get(tag_id) for tag_id in form.tags.data]
        try:
            tags_dict = {}
            tags_o = form.tags.choices.append((t.id, t.tag_name))
            tags_dict_full = tags_dict.update(tags_o)
            for tg in tags_dict_full():
                selected_tag = Tags.query.get(tg)
                db.session.add(selected_tag)
        except:
            selected_tag = None
        db.session.add(to_update_note)
        db.session.commit()
        flash('Note updated successfully!', category="success")
        return redirect(url_for('home'))
    form.body.data = to_update_note.body
    form.title.data = to_update_note.title
    form.tags.data = [tag.id for tag in to_update_note.note_tags]
    return render_template("edit.html", form=form, user=current_user, note=to_update_note)

# allows user to edit tag
@app.route('/tags/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tag(id):
    form = TagsForm()
    to_update_tag = Tags.query.get_or_404(id)
    if form.validate_on_submit():
        to_update_tag.tag_name = form.tag_name.data
        db.session.commit()
        flash('Tag updated successfully!', category="success")
        return redirect(url_for('tags'))
    form.tag_name.data = to_update_tag.tag_name
    return render_template("edit_tag.html", form=form, user=current_user, tag=to_update_tag)

# allows user to access all tags and edit or delete them
@app.route('/tags', methods=['GET', 'POST'])
@login_required
def tags():
    tags = Tags.query.order_by(Tags.id).all()
    return render_template('tags.html', tags=tags, user=current_user)

# allows user to search note's titles
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

# allows search in navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# allows user to access individual note
@app.route('/notes/<int:id>')
@login_required
def note(id):
    note = Notes.query.get_or_404(id)
    return render_template('note.html', note=note, user=current_user)

# allows user to filter notes by tags
@app.route('/tags/<tag_name>/')
@login_required
def tag(tag_name):
    tag = Tags.query.filter_by(tag_name=tag_name).first_or_404()
    return render_template('tag.html', tag=tag, user=current_user)