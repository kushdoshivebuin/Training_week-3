from django.test import TestCase
from home_app.models import Contact, User
from datetime import datetime
import pytest
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib import messages

# Create your tests here.
# Test cases for models.py file
@pytest.mark.django_db
def test_create_contact() :
    contact = Contact.objects.create(name = "testuser", email = "testuser@gmail.com", message = "This is a test message.")

    assert contact.name == "testuser"
    assert contact.email == "testuser@gmail.com"
    assert contact.message == "This is a test message."
    assert contact.timeStamp is not None
    assert isinstance(contact.timeStamp, datetime)

@pytest.mark.django_db
def test_str_contact() :
    contact = Contact.objects.create(name = "testuser", email = "testuser@gmail.com", message = "This is a test message.")

    assert str(contact) == "Message from testuser"

@pytest.mark.django_db
def test_create_user() :
    user = User.objects.create(username = "testuser", email = "testuser@gmail.com", password = "test123")

    assert user.username == "testuser"
    assert user.email == "testuser@gmail.com"
    assert user.password == "test123"
    assert user.created_at is not None
    assert isinstance(user.created_at, datetime)
    assert user.updated_at is not None
    assert isinstance(user.updated_at, datetime)

@pytest.mark.django_db
def test_str_method() :
    user = User.objects.create(username = "testuser", email = "testuser@gmail.com", password = "test123")

    assert str(user) == user.username


# Test cases for views.py file
@pytest.mark.django_db
def test_home_view(client) :
    response = client.get(reverse('home'))
    assert response.status_code == 200
    assert 'home_app/home.html' in [template.name for template in response.templates]

@pytest.mark.django_db
def test_about_view(client) :
    response = client.get(reverse('about'))
    assert response.status_code == 200
    assert 'home_app/about.html' in [template.name for template in response.templates]

@pytest.mark.django_db
def test_contact_view(client):
    response = client.get(reverse('contact'))
    assert response.status_code == 200
    assert 'home_app/contact.html' in [template.name for template in response.templates]

    data = {'name': 'Test User', 'email': 'testuser@gmail.com', 'message': 'This is a test message.'}
    response = client.post(reverse('contact'), data)

    assert response.status_code == 302  
    assert Contact.objects.filter(name="Test User").exists()

@pytest.mark.django_db
def test_login_function_view(client) :
    user = User.objects.create(username = "testuser", password = make_password("testpassword"))

    response = client.get(reverse('login'))
    assert response.status_code == 200
    assert 'home_app/login.html' in [template.name for template in response.templates]

    login_data = {'username' : 'testuser', 'password' : 'testpassword'}
    response = client.post(reverse('login'), login_data)

    assert response.status_code == 302
    assert response.url == reverse('blogHome')

    login_data_invalid = {'username' : 'testuser', 'password' : 'wrongpassword'}
    response = client.post(reverse('login'), login_data_invalid)

    assert response.status_code == 200
    assert 'Invalid username or password' in [str(m) for m in messages.get_messages(response.wsgi_request)]

@pytest.mark.django_db
def test_signup_view(client) :
    response = client.get(reverse('signup'))

    assert response.status_code == 200
    assert 'home_app/signup.html' in [template.name for template in response.templates]

    data = {
        'email' : 'testuser@gmail.com',
        'username' : 'testuser',
        'password' : 'Strongpassword123!',
        'confirm_password' : 'Strongpassword123!'
    }

    response = client.post(reverse('signup'), data)

    assert response.status_code == 302
    assert response.url == reverse('login')
    assert User.objects.filter(username = "testuser").exists()

    invalid_data = {
        'email' : 'newuser@gmail.com',
        'username' : 'newuser',
        'password' : 'Strongpassword123!',
        'confirm_password' : 'DifferentPassword456'
    }

    response = client.post(reverse('signup'), invalid_data)

    assert response.status_code == 200
    assert 'Passwords do not match!' in [str(m) for m in messages.get_messages(response.wsgi_request)]

    weak_data = {
        'email' : 'newuser@gmail.com',
        'username' : 'newuser',
        'password' : 'weak',
        'confirm_password' : 'weak'
    }

    response = client.post(reverse('signup'), weak_data)

    assert response.status_code == 200
    assert 'The password is too weak, please enter a strong password!' in [str(m) for m in messages.get_messages(response.wsgi_request)]

@pytest.mark.django_db
def test_logout_user_view(client) :
    user = User.objects.create(username = "testuser", password = make_password('testpassword'))

    client.session['username'] = user.username
    client.session.save()

    response = client.get(reverse('logout'))
    assert response.status_code == 302
    assert response.url == reverse('login')
    assert 'username' not in client.session