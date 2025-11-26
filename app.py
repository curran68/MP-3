import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

# Load env variables for local development
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

# Mongo config
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME", "recipes_db")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/recipes_db")
app.secret_key = os.environ.get("SECRET_KEY", "devsecret")

mongo = PyMongo(app)

print("Debug Mongo:")
print("URI =", app.config["MONGO_URI"])
print("DBNAME =", app.config["MONGO_DBNAME"])
print("Connection mongo.db =", mongo.db)



@app.route("/")
@app.route("/get_recipes")
def get_recipes():
    """Displays a list of all recipes."""
    recipes = list(mongo.db.recipes.find())
    return render_template("get_recipes.html", recipes=recipes)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Handles user registration."""
    if request.method == "POST":
        username = request.form.get("username").lower()

        existing_user = mongo.db.users.find_one({"username": username})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        mongo.db.users.insert_one({
            "username": username,
            "password": generate_password_hash(request.form.get("password"))
        })

        session["user"] = username
        flash("Registration Successful!")
        return redirect(url_for("profile"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login."""
    if request.method == "POST":
        username = request.form.get("username").lower()
        password = request.form.get("password")

        existing_user = mongo.db.users.find_one({"username": username})

        if existing_user and check_password_hash(existing_user["password"], password):
            session["user"] = username
            flash(f"Welcome, {username}!")
            return redirect(url_for("profile"))

        flash("Incorrect Username and/or Password")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    """Shows the currently logged-in user's profile."""
    if "user" not in session:
        flash("You need to log in to view your profile.")
        return redirect(url_for("login"))

    return render_template("profile.html", username=session["user"])


@app.route("/logout")
def logout():
    """Logs the user out."""
    flash("You have been logged out")
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    """Handles adding a new recipe."""
    if "user" not in session:
        flash("You need to log in to add a recipe.")
        return redirect(url_for("login"))

    if request.method == "POST":
        recipe = {
            "course_name": request.form.get("course_name"),
            "recipe_name": request.form.get("recipe_name"),
            "ingredients_list": request.form.get("ingredients_list"),
            "method_list": request.form.get("method_list"),
            "cook_time": request.form.get("cook_time"),
            "serves": request.form.get("serves"),
            "created_by": session["user"]
        }

        mongo.db.recipes.insert_one(recipe)
        flash("Recipe Successfully Added")
        return redirect(url_for("get_recipes"))

    # Check your collection name: ccourses vs courses
    courses = list(mongo.db.courses.find().sort("courses", 1))

    return render_template("add_recipe.html", courses=courses)


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", 5001)),
        debug=True
    )
