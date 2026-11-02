import os, requests, csv, io  # Built-in Python library for operating system functions

from cs50 import SQL  # Imports CS50's simplified database querying tool
from flask import Flask, flash, redirect, render_template, request, session, Response
from flask_session import Session  # Manages keeping users logged in safely
from werkzeug.security import check_password_hash, generate_password_hash  # Handles password encryption
from datetime import datetime, timedelta

from helpers import login_required, render_with_flash, get_hobby_image_url

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///hobby.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    """Show dashboard for user"""
    
    # Attempt to fetch a random quote
    try:
        # Send a get request to the api and wait 3 seconds maximum
        response = requests.get("https://zenquotes.io/api/random", timeout=3)
        # Translate JSON response to python list of dictionaries
        data = response.json()
        quote_text = data[0]["q"]
        quote_author = data[0]["a"]
    except Exception:
        # Fallback quote if the API request fails for any reason
        quote_text = "Small daily improvements are the key to staggering long-term results."
        quote_author = "System"
    
    # Query for user's name to remember user's name
    users_row = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    name = users_row[0]["username"]
    
    # Query for user's hobbies to show in a table
    hobbies = db.execute("SELECT id, hobby_name, measure_type, goal, image_url FROM hobbies WHERE user_id = ?", session["user_id"])
    
    # Calculate the start date of the current week (Monday at 00:00:00)
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_week_str = start_of_week.strftime("%Y-%m-%d 00:00:00")
    
    # Loop through each hobby and sum up its logs for this week
    for hobby in hobbies:
        result = db.execute(
            "SELECT SUM(amount) AS total FROM logs WHERE hobby_id = ? AND logged_at >= ?",
            hobby["id"],
            start_of_week_str
        )
    
        # If there are logs, use the sum; otherwise default to 0
        if result[0]["total"]:
            hobby["weekly_total"] = result[0]["total"]
        else:
            hobby["weekly_total"] = 0
    
    return render_template("index.html", hobbies=hobbies, name=name, quote_text=quote_text, quote_author=quote_author)
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        
        # Validate username and both passwords are not blank
        if not username:
            return render_with_flash("Username entry cannot be blank", "danger", "register.html")
        elif not password:
            return render_with_flash("Password entry cannot be blank", "danger", "register.html", username=username)
        elif password != confirmation:
            return render_with_flash("Passwords do not match", "danger", "register.html")
        
        # If all works, add user to database if he has a unique username
        hash_pass = generate_password_hash(password)
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_pass)
        except ValueError:
            return render_with_flash("Username is already taken.", "danger", "register.html")
        
        return redirect("/")
        
    
    else:
        return render_template("register.html")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    
    # Forget any user_id
    session.clear()
    
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_with_flash("You must provide a username.", "danger", "login.html")
        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_with_flash("You must provide a password.", "danger", "login.html")
        
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_with_flash("Invalid username and/or password", "danger", "login.html")
        
         # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")
        
    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/add_hobby", methods=["GET", "POST"])
@login_required
def addHobby():
    """Add new hobby"""
    if request.method == "POST":
        hobby_name = request.form.get("hobby_name")
        hobby_type = request.form.get("measure_type")
        hobby_goal = request.form.get("goal")
        # Ensure hobby name is not empty
        if not hobby_name or not hobby_name.strip():
            return render_with_flash("You must insert a valid hobby/activity", "danger", "add_hobby.html")
        # Validate hobby type
        valid_types = ["time", "units", "boolean"]
        if hobby_type not in valid_types:
            return render_with_flash("You must choose a valid metric.", "danger", "add_hobby.html")
        # Validate goal
        if not hobby_goal:
            return render_with_flash("Goal field cannot be empty.", "danger", "add_hobby.html")
        try:
            hobby_goal = int(hobby_goal)
            if hobby_goal < 1:
                return render_with_flash("Goal must be at least 1", "danger", "add_hobby.html")
        except ValueError:
            return render_with_flash("Goal must be a valid number.", "danger", "add_hobby.html")
        
        # If everything was valid, add hobby to database if it doesn't already exist
        image_url = get_hobby_image_url(hobby_name)
        try:
            db.execute("INSERT INTO hobbies (user_id, hobby_name, measure_type, goal, image_url) VALUES (?, ?, ?, ?, ?)", session["user_id"], hobby_name, hobby_type, hobby_goal, image_url)
        except ValueError:
            return render_with_flash("You already have this hobby added", "danger", "add_hobby.html")
        
        flash("You have successfully added a new hobby", "success")
        return redirect("/")
        
    else:
        return render_template("add_hobby.html")

@app.route("/delete/<int:hobby_id>", methods=["POST"])
@login_required
def delHobby(hobby_id):
    """Delete hobby"""
    
    db.execute("DELETE FROM logs WHERE hobby_id = ? AND user_id = ?", hobby_id, session["user_id"])
    db.execute("DELETE FROM hobbies WHERE id = ? AND user_id = ?", hobby_id, session["user_id"])
    flash("Hobby and associated logs deleted.", "info")
    return redirect("/")

@app.route("/log", methods=["GET", "POST"])
@login_required
def log():
    """Log new session"""
    
    if request.method == "POST":
        hobby_id = request.form.get("hobby_id")
        amount_input = request.form.get("amount")
        rating_input = request.form.get("rating")
        notes = request.form.get("notes")
        
        # Check directly if this specific hobby exists for this logged-in user
        hobby = db.execute("SELECT id FROM hobbies WHERE id = ? AND user_id = ?", hobby_id, session["user_id"])
        if not hobby_id or not hobby:
            return render_with_flash("Invalid hobby.", "danger", "log.html")
        # Validate amount exists, is a number, and is a positive integer greater than 0
        if not amount_input:
            return render_with_flash("Invalid amount.", "danger", "log.html")
        try:
            amount = int(amount_input)
            if amount < 1:
                return render_with_flash("Amount must be greater than 0.", "danger", "log.html")
        except ValueError:
            return render_with_flash("Please enter a valid integer.", "danger", "log.html")
        # Validate rating, if provided, is an integer between 1 and 10
        if rating_input:
            try:
                rating = int(rating_input)
                if rating < 1 or rating > 10:
                    return render_with_flash("Rating must be an integer between 1 and 10 inclusive", "danger", "log.html")
            except:
                return render_with_flash("Rating must be an integer", "danger", "log.html")
        
        # If everything proved valid, log session into database
        db.execute("INSERT INTO logs (user_id, hobby_id, amount, rating, notes) VALUES (?, ?, ?, ?, ?)", session["user_id"], hobby_id, amount, rating, notes)
        flash("Session logged successfully! 🚀", "success")
        return redirect("/")
                
            
        
    else:
        # Query existing user hobbies
        hobbies = db.execute("SELECT id, hobby_name, measure_type, goal, image_url FROM hobbies WHERE user_id = ?", session["user_id"])
        
        selected_hobby_id = request.args.get("hobby_id", type=int)
        return render_template("log.html", hobbies=hobbies, selected_hobby_id=selected_hobby_id)
    
@app.route("/history")
@login_required
def history():
    """Show history of logs"""
    logs = db.execute("""
               SELECT logs.id, hobbies.hobby_name, hobbies.measure_type, logs.amount, logs.logged_at, logs.rating, logs.notes 
               FROM logs
               JOIN hobbies ON logs.hobby_id = hobbies.id
               WHERE logs.user_id = ?
               ORDER BY logs.logged_at DESC""", session["user_id"])
    
    return render_template("history.html",  logs=logs)

@app.route("/export")
@login_required
def export():
    """Export user's logs into csv file"""
    
    # Query for user's logs
    logs = db.execute("""
                        SELECT logs.id, hobbies.hobby_name, hobbies.measure_type, logs.amount, logs.logged_at, logs.rating, logs.notes 
                        FROM logs
                        JOIN hobbies ON logs.hobby_id = hobbies.id
                        WHERE logs.user_id = ?
                        ORDER BY logs.logged_at DESC""", session["user_id"])
    
    # Create in-memory text buffer
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write csv header row
    writer.writerow(["Hobby", "Amount Logged", "Unit", "Data & Time", "Rating", "Notes"])
    
    # Write data rows
    for log in logs:
        writer.writerow([
            log["hobby_name"],
            log["amount"],
            log["measure_type"],
            log["logged_at"],
            log["rating"] if log["rating"] else "",
            log["notes"] if log["notes"] else ""
        ])
        
    # Return downloadable response
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=hobby_logs.csv"})

@app.route("/delete_log/<int:log_id>", methods=["POST"])
@login_required
def delete_log(log_id):
    """Delete log from database"""
    
    # Ensure that each user can delete his own logs only
    db.execute("DELETE FROM logs WHERE id = ? AND user_id = ?", log_id, session["user_id"])   
    flash("Log entry deleted.", "info")
    return redirect("/history")