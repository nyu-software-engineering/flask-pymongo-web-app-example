import pytest  # testing framework
from app import create_app  # flask app object


@pytest.fixture
def client():
    app = create_app()
    app.testing = True  # necessary for assertions to work correctly
    with app.test_client() as client:
        yield client


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


def test_create_post(client):
    """
    Test post creation
    """
    test_fname = "Test name"
    test_fmessage = "Test message"
    response = client.post(
        "/create",
        data=dict(fname=test_fname, fmessage=test_fmessage),
        follow_redirects=True,
    )
    response_data = response.data.decode()  # the HTML code
    assert response.status_code == 200, "Home route should return status code 200"
    assert test_fname in response_data, f"HTML should contain '{test_fname}'"
    assert test_fmessage in response_data, f"HTML should contain '{test_fmessage}'"
