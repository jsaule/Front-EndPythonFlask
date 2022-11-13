from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

# creates Flask instance
app = Flask(__name__)

# set configs
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "data.sqlite")
app.config['SECRET_KEY'] = 'SSDSDDSDSDSFSLGJNAOOAJGOAJNWARGAWRGAWRG'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# create database
db = SQLAlchemy()

# --------------------------------external routes----------------------------------------------------
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

# --------------------------------requiring authentication routes--------------------------------------
