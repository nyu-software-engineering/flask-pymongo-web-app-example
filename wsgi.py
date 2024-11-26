"""
Settings for how to run the app in a production environment using the WSGI standard for how web servers communicate with web applications.
See the README.md file for details on running this app in production mode.
"""

from app import app as application  # alias the Flask object temporarily

app = application  # app now refers to the Flask object

if __name__ == "__main__":
    app.run()
