# Flask-MongoDB Web App Example

![Dockerize badge](https://github.com/nyu-software-engineering/flask-pymongo-web-app-example/actions/workflows/build.yaml/badge.svg)

An example of a full-stack web application, built in Python with `flask` and `pymongo`.

## Quick test drive

The fastest way to see the example app in action on your own computer is to use [Docker](https://www.docker.com). _Note that you will not be able to edit the app code when running it this way... instructions below show you how to set up the app in a way that allows you to edit the code and see the changes._

- install and run [docker desktop](https://www.docker.com/get-started)
- create a [dockerhub](https://hub.docker.com/signup) account

Start up a MongoDB database:

- run command, `docker run --name mongodb_dockerhub -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=secret -d mongo:latest`

Start up the app:

- run command, `docker run -ti --rm -d -p 5000:5000 -e MONGO_DBNAME=flask-mongodb-web-app-example -e MONGO_URI="mongodb://admin:secret@host.docker.internal:27017/example?authSource=admin&retryWrites=true&w=majority" bloombar/flask-mongodb-web-app-example`
- if you see an error about the port number being already in use, change the first `5000` in the command to a different port number, e.g. `-p 10000:5000` to use your computer's port `10000`.

View the app in your browser:

- open a web browser and go to `http://localhost:5000` (or change `5000` to whatever port number you used in the command above)

## Setup for editing

The following instructions show you how to set up the example app on your own computer in a way that allows you to edit it.

### Build and launch the database

If you have not already done so, start up a MongoDB database:

- run command, `docker run --name mongodb_dockerhub -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=secret -d mongo:latest`

The back-end code will integrate with this database. However, it may be occasionally useful interact with the database directly from the command line:

- connect to the database server from the command line: `docker exec -ti mongodb_dockerhub mongosh -u admin -p secret`
- show the available databases: `show dbs`
- select the database used by this app: `use example`
- show the documents stored in the `messages` collection: `db.messages.find()` - this will be empty at first, but will later be populated by the app.
- exit the database shell whenever you have had your fill: `exit`

If you have trouble running Docker on your computer, use a database hosted on [MongoDB Atlas](https://www.mongodb.com/atlas) instead. Atlas is a "cloud" MongoDB database service with a free option. Create a database there, and make note of the connection string, username, password, etc.

### Create a `.env` file

A file named `.env` is necessary to run the application. This file contains sensitive environment variables holding credentials such as the database connection string, username, password, etc. This file should be excluded from version control in the [`.gitignore`](.gitignore) file.

An example file named `env.example` is given. Copy this into a file named `.env` and edit the values to match your database. If following the instructions and using Docker to run the database, the values should be:

```
MONGO_DBNAME=example
MONGO_URI="mongodb://admin:secret@localhost:27017/example?authSource=admin&retryWrites=true&w=majority"
```

The other values can be left alone.

### pip

Note that most Python programs require the use of the package manager named `pip` - the default Python "package manager". A package manager is software that takes care of installing the correct version of any modules in the correct place for the current system you are running it on. It comes with most distributions of Python. On many machines, the Python 3-compatible version it is calld `pip3` and on others it is simply `pip`... on some either works. If you are unsure, try both in the commands where you see it mentioned.

### Set up a Python virtual environment

There are multiple ways to set up a Python virtual environment - a specific area of memory and disk space where you can install the dependencies and settings necessary to run a specific app in isolation from other apps on the same computer... here are instructions for using either `pipenv` or `venv`.

### Using pipenv

The ability to make virtual environemnts with [pipenv](https://pypi.org/project/pipenv/) is relatively easy, but it does not come pre-installed with Python. It must be installed.

Install `pipenv` using `pip`:

```
pip3 install pipenv
```

Activate it:

```
pipenv shell
```

Your command line will now be running within a virtual environment.

The file named, `Pipfile` contains a list of dependencies - other Python modules that this app depends upon to run. These will have been automatically installed into the virtual environment by `pipenv` when you ran the command `pipenv shell`.

#### Using venv

If you refuse to use `pipenv` for some reason, you can use the more traditional [venv](https://docs.python.org/3/library/venv.html) instead. The ability to make virtual environments with`venv` comes included with standard Python distributions.

This command creates a new virtual environment with the name `.venv`:

```bash
python3 -m venv .venv
```

To activate the virtual environment named `.venv`...

On Mac:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate.bat
```

The `pip` settings file named, `requirements.txt` contains a list of dependencies - other Python modules that this app depends upon to run.

To install the dependencies into the currently-active virtual environment, use `pip`:

```bash
pip3 install -r requirements.txt
```

### Run the app

- define two environment variables from the command line:
  - on Mac, use the commands: `export FLASK_APP=app.py` and `export FLASK_ENV=development`.
  - on Windows, use `set FLASK_APP=app.py` and `set FLASK_ENV=development`.
- start flask with `flask run` - this will output an address at which the app is running locally, e.g. https://127.0.0.1:5000. Visit that address in a web browser.
- in some cases, the command `flask` will not be found when attempting `flask run`... you can alternatively launch it with `python3 -m flask run --host=0.0.0.0 --port=5000` (or change to `python -m ...` if the `python3` command is not found on your system).

Note that this will run the app only on your own computer. Other people will not be able to access it. If you want to allow others to access the app running on your local machine, try using the [flask-ngrok](https://pypi.org/project/flask-ngrok/) module.
