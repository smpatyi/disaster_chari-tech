import flask
import os

from flask_login import current_user, login_user, LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)

# using flask login in order to manage the users logging in to the site
login_manager = LoginManager()
login_manager.init_app(app)

# initializing the database
db = SQLAlchemy(app)

# data model for users
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(16))
    password = db.Column(db.String(20))


# creating the database
db.create_all()

# app route for the main page that is what is seen first when app is opened
@app.route("/", methods=["GET", "POST"])
def welcome():
    if flask.request.method == "POST":
        # checks if the button pressed is the one for login; if yes, redirects to new HTML page
        if request.form.get("log_in") == "Login":
            return flask.redirect(flask.url_for("log_in"))
        # checks if the button pressed is the one for sign up; if yes, redirects to new HTML page
        elif request.form.get("sign_up") == "Sign Up":
            return flask.redirect(flask.url_for("sign_up"))
    return flask.render_template(
        "index.html",
    )


# @app.route("/log_in", methods=["GET", "POST"])
# def log_in():
#     if flask.request.method == "POST":
#         data = flask.request.form
#         user_name = data["user_name"]
#         password = data["password"]

#         # error handling for arbitrary length of inputted username and password
#         if len(user_name) > 16:
#             flask.flash("User name too long. Please enter a new one.")
#             return flask.redirect(flask.url_for("log_in"))
#         if len(password) > 20:
#             flask.flash("Password is too long. Please enter a new one.")
#             return flask.redirect(flask.url_for("log_in"))

#         # check if it is a unique username that already exists in database
#         if "user_name" in data:
#             user = User.query.filter_by(user=data["user_name"]).first()
#             if user is None:
#                 return flask.redirect(flask.url_for("sign_up"))
#             else:
#                 login_user(user)
#                 return flask.redirect(flask.url_for("index"))

#     return flask.render_template(
#         "log_in.html",
#     )


@login_manager.user_loader
def get_user(user_id):
    return User.query.get(int(user_id))


app.run(
    host=os.getenv("IP", "0.0.0.0"), port=int(os.getenv("PORT", "8080")), debug=True
)
