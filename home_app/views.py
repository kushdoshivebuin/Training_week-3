from django.shortcuts import render, HttpResponse, redirect
from home_app.models import Contact, User
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
import zxcvbn  # Password strength checker library

# Render the home page
def home(request):
    """
    Renders the home page view.

    This is the landing page that users see when they visit the site.
    """
    return render(request, 'home_app/home.html')

# Render the about page
def about(request):
    """
    Renders the about page view.

    Displays information about the website or the company.
    """
    return render(request, 'home_app/about.html')

# Handle contact form submissions
def contact(request):
    """
    Processes the contact form. Validates the input and stores the message
    in the database if it's correct. If not, displays an error message.

    POST request: Retrieves form data, validates it, and stores the contact
    information in the database if it's valid.
    """
    if request.method == 'POST':
        # Retrieve form input from POST request
        user_cname = request.POST['name']
        user_cemail = request.POST['email']
        user_cmessage = request.POST['message']

        # Validate form data (simple checks for length)
        if len(user_cname) <= 2 or len(user_cemail) <= 3 or len(user_cmessage) <= 4:
            messages.error(request, "Please fill the form correctly!")  # Display error message
        else:
            # Save contact message to the database
            contact = Contact(name=user_cname, email=user_cemail, message=user_cmessage)
            contact.save()
            messages.success(request, "We will get back to you soon!")  # Success message
            return redirect('home')
    return render(request, 'home_app/contact.html')

# Categorize password strength using zxcvbn
def categorize_password(password):
    """
    Analyzes the strength of a password using the zxcvbn library.

    The password strength is evaluated and classified based on its score:
    - Easy: score 0 or 1
    - Medium: score 2
    - Hard: score 3 or 4
    
    Parameters:
    password (str): The password string to be analyzed.

    Returns:
    str: A classification of the password strength.
    """
    result = zxcvbn.zxcvbn(password)
    print(result)
    # Classify password strength based on the score from zxcvbn
    score = result['score']
    if score == 0 or score == 1:
        return "Easy"
    elif score == 2:
        return "Medium"
    elif score == 3 or score == 4:
        return "Hard"

# User login functionality
def login_function(request):
    """
    Handles user login. Validates the entered username and password.
    Sets the user session on successful login.

    POST request: Retrieves username and password, validates them, and logs the user in.
    """
    if request.method == 'POST':
        lusername = request.POST['username']
        user_lpassword = request.POST['password']

        # Attempt to fetch the user by username
        try:
            user = User.objects.get(username=lusername)  # Fetch the user based on username
        except User.DoesNotExist:
            messages.error(request, "Invalid username or password")  # Error message if user not found
            return render(request, 'home_app/login.html')

        # Check if entered password matches the stored hashed password
        if check_password(user_lpassword, user.password):  # Password verification
            # Save username in session to maintain login state
            request.session['username'] = user.username
            return redirect('blogHome')  # Redirect to the blog home page after successful login
        else:
            messages.error(request, "Invalid username or password")  # Error message for wrong password

    return render(request, 'home_app/login.html')

# User signup functionality
def signup(request):
    """
    Handles the user signup process. Validates email, username, password, and ensures
    the password strength is acceptable.

    POST request: Validates the form fields, checks password strength, and creates a new user
    if all conditions are met. Redirects to the login page after successful signup.
    """
    if request.method == 'POST':
        # Retrieve form input
        semail_address = request.POST['email']
        susername = request.POST['username']
        suser_password = request.POST['password']
        sconfirm_password = request.POST['confirm_password']

        # Validate password confirmation
        if suser_password != sconfirm_password:
            messages.error(request, "Passwords do not match!")  # Error message if passwords don't match
            return render(request, 'home_app/signup.html')

        # Check if username already exists
        elif User.objects.filter(username=susername).exists():
            messages.error(request, "Username has already been taken.")  # Error if username exists
            return render(request, 'home_app/signup.html')
        
        # Check if email already exists
        elif User.objects.filter(email=semail_address).exists():
            messages.error(request, "Email address has already been taken.")  # Error if email exists
            return render(request, 'home_app/signup.html')

        # Check password strength using the categorize_password function
        strength = categorize_password(suser_password)

        if strength == "Easy":
            messages.error(request, "The password is too weak, please enter a strong password!")
            return render(request, 'home_app/signup.html')  # Redirect if password is too weak
        
        else:
            # Hash the password and save the new user
            user = User(email=semail_address, username=susername, password=make_password(suser_password))
            user.save()
            return redirect('login')  # Redirect to login after successful signup

    return render(request, 'home_app/signup.html')

# User logout functionality
def logoutUser(request):
    """
    Logs out the user by clearing their session.

    Clears the user's session to log them out and redirects to the login page.
    """
    request.session.flush()  # Clears the entire session
    return redirect("/login")  # Redirect to login page after logout

# Forgot password page (no logic yet)
def forgot_password(request):
    """
    Renders the forgot password page.

    This page allows users to request a password reset. It currently has no logic implemented.
    """
    return render(request, 'home_app/forgot_password.html')
