from flask import Flask, render_template

# creates Flask instance
app = Flask(__name__)

# --------------------------------external routes----------------------------------------------------
@app.route('/aboutus')
def aboutus():
    return render_template("aboutus.html")

# --------------------------------requiring authentication routes----------------------------------------------------