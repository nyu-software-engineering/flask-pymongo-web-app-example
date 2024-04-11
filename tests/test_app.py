import pytest  # testing framework
import datetime
from app import create_app  # flask app object

# unique data for any test post
random_text = datetime.datetime.now().time()  # current date/time
test_fname = f"Test name {random_text}"
test_fmessage = f"Test message {random_text}"


@pytest.fixture
def client():
    """
    Create and yield Flask app
    """
    app = create_app()
    app.testing = True  # necessary for assertions to work correctly
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="function")
def test_post(client):
    """
    Create and remove a test post saved in the database
    """
    # create the post
    response = client.post(
        "/create",
        data=dict(fname=test_fname, fmessage=test_fmessage),
        follow_redirects=True,
    )
    yield response
    # delete the post
    response = client.post(
        f"/delete-by-content/{test_fname}/{test_fmessage}",
        follow_redirects=True,
    )


def test_home_status(client):
    response = client.get("/")  # make get request for home route
    assert response.status_code == 200, "Home route should return status code 200"


def test_home_templating(client):
    """
    Verify that the base template with header and footer is loading
    """
    response = client.get("/")  # make get request for home route
    response_data = response.data.decode()  # the HTML code
    assert "<header>" in response_data, "HTML should contain <header>"
    assert "<footer>" in response_data, "HTML should contain <footer>"


def test_home_content(client):
    """
    Verify that the home page static content is loading
    """
    response = client.get("/")  # make get request for home route
    response_data = response.data.decode()  # the HTML code
    assert "<h2>Posts</h2>" in response_data, "HTML should contain <h2>Posts</h2>"


def test_create_post(client, test_post):
    """
    Test post creation
    """
    response_data = test_post.data.decode()  # the HTML code
    assert test_post.status_code == 200, "Home route should return status code 200"
    assert test_fname in response_data, f"HTML should contain '{test_fname}'"
    assert test_fmessage in response_data, f"HTML should contain '{test_fmessage}'"


#
# these test are not exhaustive
# they should include tests for the /create, /edit, /delete routes
# this requires refactoring the code to make it more easily testable, which is standard practice
#
