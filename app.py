#!/usr/bin/env python3

"""
Example flask-based web application.
See the README.md file for instructions how to set up and run the app in development mode.
"""

import os
import datetime
from flask import Flask, render_template, request, redirect, url_for
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv, dotenv_values

load_dotenv()  # load environment variables from .env file


def create_app():
    """
    Create and configure the Flask application.
    returns: app: the Flask application object
    """

    app = Flask(__name__)
    # load flask config from env variables
    config = dotenv_values()
    app.config.from_mapping(config)

    cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = cxn[os.getenv("MONGO_DBNAME")]

    try:
        cxn.admin.command("ping")
        print(" *", "Connected to MongoDB!")
    except Exception as e:
        print(" * MongoDB connection error:", e)

    @app.route("/")
    def home():
        """
        Route for the home page.
        Returns:
            rendered template (str): The rendered HTML template.
        """
        docs = db.messages.find({}).sort("created_at", -1)
        return render_template("index.html", docs=docs)

    @app.route("/create", methods=["POST"])
    def create_post():
        """
        Route for POST requests to the create page.
        Accepts the form submission data for a new document and saves the document to the database.
        Returns:
            redirect (Response): A redirect response to the home page.
        """
        name = request.form["fname"]
        message = request.form["fmessage"]

        doc = {
            "name": name,
            "message": message,
            "created_at": datetime.datetime.utcnow(),
        }
        db.messages.insert_one(doc)

        return redirect(url_for("home"))

    @app.route("/edit/<post_id>")
    def edit(post_id):
        """
        Route for GET requests to the edit page.
        Displays a form users can fill out to edit an existing record.
        Args:
            post_id (str): The ID of the post to edit.
        Returns:
            rendered template (str): The rendered HTML template.
        """
        doc = db.messages.find_one({"_id": ObjectId(post_id)})
        return render_template("edit.html", doc=doc)

    @app.route("/edit/<post_id>", methods=["POST"])
    def edit_post(post_id):
        """
        Route for POST requests to the edit page.
        Accepts the form submission data for the specified document and updates the document in the database.
        Args:
            post_id (str): The ID of the post to edit.
        Returns:
            redirect (Response): A redirect response to the home page.
        """
        name = request.form["fname"]
        message = request.form["fmessage"]

        doc = {
            "name": name,
            "message": message,
            "created_at": datetime.datetime.utcnow(),
        }

        db.messages.update_one({"_id": ObjectId(post_id)}, {"$set": doc})

        return redirect(url_for("home"))

    @app.route("/delete/<post_id>")
    def delete(post_id):
        """
        Route for GET requests to the delete page.
        Deletes the specified record from the database, and then redirects the browser to the home page.
        Args:
            post_id (str): The ID of the post to delete.
        Returns:
            redirect (Response): A redirect response to the home page.
        """
        db.messages.delete_one({"_id": ObjectId(post_id)})
        return redirect(url_for("home"))

    @app.route("/delete-by-content/<post_name>/<post_message>", methods=["POST"])
    def delete_by_content(post_name, post_message):
        """
        Route for POST requests to delete all post by their author's name and post message.
        Deletes the specified record from the database, and then redirects the browser to the home page.
        Args:
            post_name (str): The name of the author of the post.
            post_message (str): The contents of the message of the post.
        Returns:
            redirect (Response): A redirect response to the home page.
        """
        db.messages.delete_many({"name": post_name, "message": post_message})
        return redirect(url_for("home"))

    @app.errorhandler(Exception)
    def handle_error(e):
        """
        Output any errors - good for debugging.
        Args:
            e (Exception): The exception object.
        Returns:
            rendered template (str): The rendered HTML template.
        """
        return render_template("error.html", error=e)

    return app


app = create_app()

if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    FLASK_ENV = os.getenv("FLASK_ENV")
    print(f"FLASK_ENV: {FLASK_ENV}, FLASK_PORT: {FLASK_PORT}")

    app.run(port=FLASK_PORT)
