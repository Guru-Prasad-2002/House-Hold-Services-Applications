from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db
from .models import Admin, Service_Professional, Customer, Service
from flask_login import login_user, login_required, logout_user, current_user 
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Blueprint has a bunch of routes/urls inside it

auth = Blueprint('auth', __name__, template_folder='templates',
    static_folder='static')

@auth.route('/',methods=['GET','POST'])
def click_here_button():
    if not Admin.query.first():
        admin = Admin(email="admin@gmail.com", password=generate_password_hash("admin@2002"))
        # Add the admin user to the session and commit to the database
        db.session.add(admin)
        db.session.commit()
    return render_template('click_here_button.html')

@auth.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email_id = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        if not role:
            return "Please select a role", 400  # You can handle this error more gracefully if needed

        if role == 'admin':
            user = Admin.query.filter_by(email=email_id).first()
            if user and check_password_hash(user.password,password):
                login_user(user, remember=False)
                return redirect(url_for('admin.home'))

        if role == 'service_professional':
            user = Service_Professional.query.filter_by(email=email_id).first()
            if user and check_password_hash(user.password,password):
                login_user(user, remember=False)
                return redirect(url_for('service_professional.home'))  # Change this route as needed

        if role == 'customer':
            user = Customer.query.filter_by(email=email_id).first()
            if user and check_password_hash(user.password,password):
                login_user(user, remember=False)
                return redirect(url_for('customers.home'))

        flash('Invalid Credentials or Role', 'danger')

    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    # Fetch service names from the Service table
    service_options = Service.query.with_entities(Service.name).all()

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')  # Get the selected role

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match", 'danger')
            return redirect(url_for('auth.signup'))

        # Check if user already exists
        user = Service_Professional.query.filter_by(email=email).first() or \
            Customer.query.filter_by(email=email).first()

        if user:
            flash("Email is already registered", 'danger')
            return redirect(url_for('auth.signup'))

        # Create user based on role
        if role == 'service_professional':
            name = request.form.get('name')
            service_type = request.form.get('service_type')  # Get the selected service type
            experience = request.form.get('experience')
            description = request.form.get('description')
            location = request.form.get('location')
            pin_code = request.form.get('pin_code')

            # Fetch the Service ID for the selected service type
            service = Service.query.filter_by(name=service_type).first()
            if not service:
                flash("Invalid service type selected", 'danger')
                return redirect(url_for('auth.signup'))

            new_user = Service_Professional(
                email=email, 
                password=generate_password_hash(password),
                name=name,
                service_type_id=service.id,  # Use the service ID here
                experience=experience,
                description=description,
                location=location,
                pin_code=pin_code,
            )

        elif role == 'customer':
            new_user = Customer(email=email, password=generate_password_hash(password))
        else:
            flash("Invalid role selected", 'danger')
            return redirect(url_for('auth.signup'))

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Log the user in after successful registration
        login_user(new_user, remember=False)

        # Redirect to the appropriate home page based on the user's role
    
        if role == 'service_professional':
            return redirect(url_for('service_professional.home'))
        else:
            return redirect(url_for('customers.home'))

    # Pass service options to the template
    return render_template('signup.html', service_options=service_options)

@auth.route('/logout')
@login_required 
def logout():
    logout_user()  # Log out the current user
    # session.clear()
    return redirect(url_for('auth.login')) 