# adding __init__.py makes website folder a seperate python package
from flask import Flask
from os import path
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__) 

    app.config['SECRET_KEY'] = 'Any Random String' # used in hashing session and cookie data
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

    db.init_app(app)
    
    from .admin import admin
    from .auth import auth
    from .service_professional import service_professional
    from .customers import customers
    from .models import Admin, Service_Professional, Customer

    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(customers, url_prefix='/customers')
    app.register_blueprint(service_professional, url_prefix='/service_professional')
    app.register_blueprint(auth, url_prefix='/')

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' # we are telling login manager where the user has to be redirected if he is not logged in
    login_manager.init_app(app) #we are telling flask login manager what app we are using


    @login_manager.user_loader
    def load_user(user_id):
    # Return None if the user_id is None or an empty string
        if not user_id:
            return None

        # Try to load the user from each table by primary key
        admin_user = Admin.query.get(user_id)
        if admin_user:
            return admin_user
        
        service_professional_user = Service_Professional.query.get(user_id)
        if service_professional_user:
            return service_professional_user
        
        customer_user = Customer.query.get(user_id)
        if customer_user:
            return customer_user
        
        return None
    return app

def create_database(app):
    if not path.exists('./website/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('Created Database!')
            # Create the admin user

            print('Admin user created!')

