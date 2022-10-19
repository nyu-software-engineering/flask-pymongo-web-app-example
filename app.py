#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, make_response
from dotenv import dotenv_values
import pymongo
import datetime
from bson.objectid import ObjectId

# modules useful for user authentication
import flask_login
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

# instantiate the app
app = Flask(__name__)
app.secret_key = 'secret'  # Change this!

# set up flask-login for user authentication
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# load credentials and configuration options from .env file
# if you do not yet have a file named .env, make one based on the template in env.example
config = dotenv_values(".env")

# turn on debugging if in development mode
if config['FLASK_ENV'] == 'development':
    # turn on debugging, if in development
    app.debug = True # debug mnode

# connect to the database
cxn = pymongo.MongoClient(config['MONGO_URI'], serverSelectionTimeoutMS=5000)
try:
    # verify the connection works by pinging the database
    cxn.admin.command('ping') # The ping command is cheap and does not require auth.
    db = cxn[config['MONGO_DBNAME']] # store a reference to the database
    print(' *', 'Connected to MongoDB!') # if we get here, the connection worked!
except Exception as e:
    # the ping command failed, so the connection is not available.
    # render_template('error.html', error=e) # render the edit template
    print(' *', "Failed to connect to MongoDB at", config['MONGO_URI'])
    print(' * ', 'Database connection error:', e) # debug


# a class to represent a user
class User(flask_login.UserMixin):
    # inheriting from the UserMixin class gives this blank class default implementations of the necessary methods that flask-login requires all User objects to have
    # see some discussion of this here: https://stackoverflow.com/questions/63231163/what-is-the-usermixin-in-flask
    def __init__(self, data):
        '''
        @param data: a dictionary containing the user's data pulled from the database
        '''
        self.id = data['_id']
        self.data = data

def locate_user(user_id=None, email=None):
    '''
    Return a User object for the user with the given id or email address, or None if no such user exists.
    @param user_id: the user_id of the user to locate
    @param email: the email address of the user to locate
    '''
    if user_id:
        # loop up by user_id
        criteria = {"_id": ObjectId(user_id)}
    else:
        # loop up by email
        criteria = {"email": email}
    doc = db.users.find_one(criteria) # find a user with this email

    # if user exists in the database, create a User object and return it
    if doc:
        # return a user object representing this user
        user = User(doc)
        return user
    # else
    return None

@login_manager.user_loader
def user_loader(user_id):
    ''' 
    This function is called automatically with every request the browser makes to the server.
    If there is an existing session, meaning the user has already logged in, then this function will return the logged-in user's data.
    @param user_id: the user_id of the user to load
    '''
    return locate_user(user_id=user_id) # return a User object if a user with this user_id exists

# set up the routes

# route for the home page
@app.route('/')
def home():
    """
    Route for the home page
    """
    docs = db.exampleapp.find({}).sort("created_at", -1) # sort in descending order of created_at timestamp
    return render_template('index.html', docs=docs) # render the hone template

# route to accept form submission and create a new post
@app.route('/create', methods=['POST'])
def create_post():
    """
    Route for POST requests to the create page.
    Accepts the form submission data for a new document and saves the document to the database.
    """
    name = request.form['fname']
    message = request.form['fmessage']


    # create a new document with the data the user entered
    doc = {
        "name": name,
        "message": message, 
        "created_at": datetime.datetime.utcnow()
    }
    db.exampleapp.insert_one(doc) # insert a new document

    return redirect(url_for('home')) # tell the browser to make a request for the / route (the home function)


# route to view the edit form for an existing post
@app.route('/edit/<mongoid>')
def edit(mongoid):
    """
    Route for GET requests to the edit page.
    Displays a form users can fill out to edit an existing record.
    """
    doc = db.exampleapp.find_one({"_id": ObjectId(mongoid)})
    return render_template('edit.html', mongoid=mongoid, doc=doc) # render the edit template


# route to accept the form submission to delete an existing post
@app.route('/edit/<mongoid>', methods=['POST'])
def edit_post(mongoid):
    """
    Route for POST requests to the edit page.
    Accepts the form submission data for the specified document and updates the document in the database.
    """
    name = request.form['fname']
    message = request.form['fmessage']

    doc = {
        # "_id": ObjectId(mongoid), 
        "name": name, 
        "message": message, 
        "created_at": datetime.datetime.utcnow()
    }

    db.exampleapp.update_one(
        {"_id": ObjectId(mongoid)}, # match criteria
        { "$set": doc }
    )

    return redirect(url_for('home')) # tell the browser to make a request for the / route (the home function)

# route to delete a specific post
@app.route('/delete/<mongoid>')
def delete(mongoid):
    """
    Route for GET requests to the delete page.
    Deletes the specified record from the database, and then redirects the browser to the home page.
    """
    db.exampleapp.delete_one({"_id": ObjectId(mongoid)})
    return redirect(url_for('home')) # tell the web browser to make a request for the / route (the home function)

# route to show a signup form to the user
@app.route('/signup', methods=['GET'])
def signup():
    return '''
            <form action='signup' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='submit' name='submit' value='Sign up'/>
            </form>
            '''

# route to handle the submission of the login form
@app.route('/signup', methods=['POST'])
def signup_submit():
    email = request.form['email']
    password = request.form['password']
    hashed_password = generate_password_hash(password)
    mongo_id = db.users.insert_one({"email": email, "password": hashed_password}).inserted_id # hash the password and save it to the database

    if mongo_id:
        # successfully created a new user
        user = User({
            "_id": mongo_id,
            "email": email,
            "password": hashed_password
        })
        flask_login.login_user(user)
        return redirect(url_for('protected'))
    # else
    return 'Signup failed'

# route to show a login form to the user
@app.route('/login', methods=['GET'])
def login():
    return '''
            <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='submit' name='submit' value='Log in'/>
            </form>
            '''

# route to handle the submission of the login form
@app.route('/login', methods=['POST'])
def login_submit():
    email = request.form['email']
    password = request.form['password']
    user = locate_user(email=email) # load up any existing user with this email address from the database
    # check whether the password the user entered matches the hashed password in the database
    if user and check_password_hash(user.data['password'], password):
        flask_login.login_user(user)
        return redirect(url_for('protected'))
    # else
    return 'Login failed'

# route to logout a user
@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'

# example of a route that requires the user to be logged in to access
@app.route('/protected')
@flask_login.login_required
def protected():
    current_user = flask_login.current_user
    return 'You are logged in as user {email}. Welcome!'.format(email=current_user.data['email'])

# route to handle any errors
@app.errorhandler(Exception)
def handle_error(e):
    """
    Output any errors - good for debugging.
    """
    return render_template('error.html', error=e) # render the edit template


# run the app
if __name__ == "__main__":
    #import logging
    #logging.basicConfig(filename='/home/ak8257/error.log',level=logging.DEBUG)
    app.run(debug = True)
