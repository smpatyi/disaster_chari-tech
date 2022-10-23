import flask
import os
import re

from os import getenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    login_required,
    login_user,
    logout_user,
    current_user,
)
from flask_sqlalchemy import SQLAlchemy=
from dotenv import find_dotenv, load_dotenv
from passlib.hash import sha256_crypt

app = flask.Flask(__name__)

load_dotenv(find_dotenv())

app.secret_key = os.getenv("SECRET_KEY")
# pointing flask app towards heroku database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
# Gets rid of a warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# loop in order to change the config variables for the heroku app to access the database
if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgres://"):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config[
        "SQLALCHEMY_DATABASE_URI"
    ].replace("postgres://", "postgresql://")

# initializing the database
db = SQLAlchemy(app)

# using flask login in order to manage the users logging in to the site
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "main"


# data model for users
class UserLogin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return "<User %r>" % self.user

    def get_username(self):
        return self.user


# uses login manager to help handle user input
@login_manager.user_loader
def load_user(user_id):
     return UserLogin.query.get(int(user_id))


# creating the database
with app.app_context():
      db.create_all()

# app route for the main page that is what is seen first when app is opened
@app.route("/", methods=["GET"])
def main():
    return flask.render_template(
        "main.html",
    )


# separate route because the first should just be the display, while this handles button clicks
@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    if flask.request.method == "POST":
        # checks if the button pressed is the one for login; if yes, redirects to new HTML page
        if request.form.get("log_in") == "Login":
            return flask.redirect(flask.url_for("log_in"))
        # checks if the button pressed is the one for sign up; if yes, redirects to new HTML page
        elif request.form.get("sign_up") == "Sign Up":
            return flask.redirect(flask.url_for("sign_up"))


# displays log in page with input forms
@app.route("/log_in", methods=["GET"])
def log_in():
    return flask.render_template(
        "log_in.html",
    )



@app.route("/logged_in", methods=["GET", "POST"])
def logged_in():
    if flask.request.method == "POST":
        login_username = flask.request.form.get("user_name")

        # error handling for arbitrary length of inputted username and password
        if len(login_username) > 20:
            flask.flash("Input too long. Try again.")
            return flask.redirect(flask.url_for("log_in"))

        user = UserLogin.query.filter_by(user=login_username).first()

        if user:
            if sha256_crypt.verify(
                flask.request.form.get("password"),
                UserLogin.query.filter_by(user=flask.request.form.get("user_name"))
                .first()
                .password,
            ):
                login_user(user)
                return flask.redirect(flask.url_for("main"))
            else:
                flask.flash("No account found with that username. Please sign up.")
                return flask.redirect(flask.url_for("sign_up"))
        else:
            flask.flash("No account found with that username. Please sign up.")
            return flask.redirect(flask.url_for("sign_up"))


# app route for displaying the forms and input info on the sign up page
@app.route("/sign_up", methods=["GET"])
def sign_up():
    return flask.render_template("sign_up.html")


# app route for handling database entry creation for sign up
@app.route("/signed_up", methods=["GET", "POST"])
def signed_up():
    if flask.request.method == "POST":
        data = flask.request.form
        user_name = data["user_name"]
        password = data["password"]

        # error handling for arbitrary length of inputted username and password
        if len(user_name) > 20:
            flask.flash("User name incorrect. Please enter the correct one.")
            return flask.redirect(flask.url_for("sign_up"))
        if len(password) > 20:
            flask.flash("Password incorrect. Please enter the correct one.")
            return flask.redirect(flask.url_for("sign_up"))

        # check if it is a unique username that already exists in database
        if "user_name" in data:
            username_input = flask.request.form.get("user_name")
            user = UserLogin.query.filter_by(user=username_input).first()
            if user is None:
                password_input = flask.request.form.get("password")
                password_encrypted = sha256_crypt.encrypt(password_input)
                new_user = UserLogin(
                    user=username_input,
                    password=password_encrypted,
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return flask.redirect(flask.url_for("main"))
            else:
                flask.flash("Account already exists. Please log in.")
                return flask.redirect(flask.url_for("log_in"))


@app.route("/volunteer", methods=["GET", "POST"])
def volunteer():
    return flask.render_template("Volunteer.html")

@app.route("/charities", methods=["GET", "POST"])
def charities():
    return flask.render_template("charities.html")

@app.route("/aboutUs", methods=["GET", "POST"])
def about():
    return flask.render_template("aboutUs.html")

@app.route("/hurricane", methods=["GET", "POST"])
def hurricane():
    return flask.render_template("hurricane.html")

@app.route("/brazil", methods=["GET", "POST"])
def brazil():
    return flask.render_template("brazil.html")

@app.route("/flint", methods=["GET", "POST"])
def flint():
    return flask.render_template("flint.html")

@app.route("/charityOne", methods=["GET", "POST"])
def charityOne():
    return flask.render_template("charityOne.html")

# handles logic to log user out of app
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return flask.redirect("/")


app.run(
    host=os.getenv("IP", "0.0.0.0"), port=int(os.getenv("PORT", "8080")), debug=True
)
