from flask_wtf import FlaskForm
from wtforms.widgets import TextArea
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class SignUpForm(FlaskForm):
    '''A form to let users sign up'''
    name = StringField('First name', validators=[DataRequired(), Length(0, 64)])
    email = EmailField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo("confirm_password", message="Passwords do not match.")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    '''A form to let users to log in'''
    email = EmailField('Email', validators=[DataRequired(), Length(0, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class NotesForm(FlaskForm):
    '''A form to let users write a note'''
    title = StringField('Write new note:', validators=[DataRequired()])
    body = StringField('Note', validators=[DataRequired()], widget=TextArea())
    submit = SubmitField('Submit')

class TagsForm(FlaskForm):
    '''A form to let users create tags'''
    tag_name = StringField("Tag", validators=[DataRequired()])
    submit_c = SubmitField("Submit")