from flask import Flask, redirect, url_for, request, render_template, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask (__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3' # users is the name of table that will be referenced, if not existent it creates file 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=1) 


db = SQLAlchemy(app)

class users(db.Model): #define the properties that are to be saved
    _id = db.Column("id", db.Integer, primary_key=True)  #every single object needs an identification in SQL, needs to be unique, don't duplicate in errors
    name = db.Column(db.String(100)) # define the type and # of characters
    email = db.Column(db.String(100)) #define the type and # of characters

    def __init__(self, name, email):
        self.name = name
        self.email = email

@app.route("/")
def home():
    return render_template("index.html", content=["Kelli", "Chris"])

@app.route("/login", methods=["POST", "GET"])   #build login page using HTML form
def login():
    if request.method == "POST": #If we have received a POST request that means we submitted the form and should redirect to the appropriate page. Otherwise we should simply return and render the login page.
        session.permanent = True
        user = request.form # use the name(nm) as a dictionary key on request.form
        userName=user['nm']
        userEmail=user['email']
        session["user"] = user

        found_user = users.query.filter_by(name=userName).first() # will find all users in table that have certain name then grab save or whatever you want to do
        if found_user:    # if user exists in database
            session["email"] = found_user.email
        else:
            userObject=users(userName,userEmail)
            db.session.add(userObject)    # here it waits to be finally saved to database
            db.session.commit()     #rollback changes

#Note: #found_user = users.query.filter_by(name=user).delete() # this is to how to delete an object
#for user in found_user: #this would delete all
#user.delete() 

        flash("Login Successful!")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already Logged In!")
            return redirect(url_for("user"))
        
        return render_template("login.html")
    
@app.route("/user", methods=["POST", "GET"]) 
def user():
    email = None
    if "user" in session:
        user = session["user"]
        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = users.query.filter_by(name=user).first()   # when email is posted, you want to try to find specific user and save the new email
            found_user.email = email # change users email
            db.session.commit()    # if want to save changes
            flash("Email was saved!")

        else:
            if "email" in session:
                email = session["email"]

        return render_template("user.html", email=email)
    else:
        flash("You are not logged in!")
        return redirect (url_for("login"))
    
@app.route("/logout")
def logout():
    if "user" in session:     # here you check if the dictionary key exists    # basicallly store and retrieve session data
        user = session["user"]
        flash("You have been logged out!", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))

@app.route("/<name>")
def greetingToUser (name):
    return f"Hello {name}!"

@app.route("/admin")
def admin():
    return redirect(url_for("home"))

@app.route("/test")
def test():
    return render_template("new.html")

@app.route("/reset")
def reset():
    with app.app_context():
        db.drop_all()
        db.create_all()
    return "DATABASE RESET"    


if __name__== "__main__":
    with app.app_context(): #Flask needs an active application context to know which app’s configuration and resources (like the database) to use when you run code outside of handling a web request.
        db.create_all()
    app.run(debug=True)

