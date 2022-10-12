#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, make_response
from dotenv import dotenv_values

import pymongo
import datetime
from bson.objectid import ObjectId
import sys

# instantiate the app
app = Flask(__name__)

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
    print('Database connection error:', e) # debug

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
