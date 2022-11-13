from flask import Flask, render_template

# creates Flask instance
app = Flask(__name__)

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
