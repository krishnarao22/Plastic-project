import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

# Lines 11 - 26 credit CS50
# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///plastic.db")


# global vars needed later
units_dict = {1: "Unit 1"}
unit_rqst = None
source_dict = {}


# Routing

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "GET":
        return render_template("login.html")
    else:
        if not request.form.get("username"):
            return("You must enter a username!")
        elif not request.form.get("password"):
            return("You must enter a password!")
        else:
            # Validate user
            rows = db.execute("SELECT * from users WHERE username = :username", username=request.form.get("username"))
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                return "Invalid username or password!"
            else:
                session["user_id"] = rows[0]["id"]
                global lang
                lang = db.execute("SELECT lang FROM users WHERE id=:uid", uid = session["user_id"])
                return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        if not request.form.get("username"):
            return("You must enter a username")
        elif not request.form.get("password"):
            return("You must enter a password")
        elif not request.form.get("password_confirm"):
            return("You must enter a password")
        else:
            if len(db.execute("SELECT username FROM users WHERE username=:username", username=request.form.get("username"))) != 0:
                return("This username is already taken!")
            elif request.form.get("password") != request.form.get("password_confirm"):
                return("Your passswords did not match!")
            else:
                pw_hash=generate_password_hash(request.form.get("password"))
                print(request.form.get("lang"))
                db.execute("INSERT INTO users (username, hash, level, lang) VALUES (:username, :pw, 0, :lang)", username=request.form.get("username"), pw=pw_hash, lang=request.form.get("lang"))
                return redirect("/")

@app.route("/instr")
def instr():
    return render_template("instructions.html")

@app.route("/activities", methods=["GET", "POST"])
def act():
    if request.method == "GET":
        return render_template("activities.html", u1 = units_dict)
    else:
        global unit_rqst
        unit_rqst = request.form.get("unit")
        return redirect("/information") # FIND A WAY TO PASS ON THE REQUESTED UNIT

@app.route("/information", methods=["GET", "POST"])
def info():
    if request.method == "GET":
        global unit_rqst
        print(unit_rqst)
        maintxt = db.execute("SELECT point_text FROM :tbl", tbl = unit_rqst + "_info")
        for i in range(0, len(maintxt)):
            maintxt[i] = maintxt[i]['point_text']
        return render_template("information.html", maintxt=maintxt)
    elif request.method == "POST":
        print(request.form.get("continue"))
        if request.form.get("continue") == "y":
            return redirect("/q1")

@app.route("/q1", methods=["GET", "POST"])
def q1():
    if request.method == "GET":
        # need to pass question and options
        quest = db.execute("SELECT question FROM :tbl WHERE q_id='1'", tbl = unit_rqst + "_q")
        quest = quest[0]['1']
        opt_list = db.execute("SELECT opt1, opt2, opt3, opt4 FROM :tbl WHERE q_id='1'", tbl = unit_rqst + "_q")
        print(opt_list)
        return render_template("q1.html");