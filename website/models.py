from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from . import db
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID


# Admin Model (No changes made to this)
class Admin(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def __str__(self):
        return f"Admin(id={self.id}, email={self.email})"

# Customer Model
class Customer(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(50), default='UnBlocked')  ## UnBlocked, Blocked

    def __str__(self):
        return f"Customer(id={self.id}, email={self.email})"

# Service Professional Model
class Service_Professional(UserMixin, db.Model):
    __tablename__ = 'service_professional'  # Explicit table name
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    service_type_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)  # Foreign key to Service
    experience = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)  # Location of the service professional
    pin_code = db.Column(db.String(10), nullable=True)  # Pin code of the service professional
    status = db.Column(db.String(50), default='Pending')  # Pending, Approved, Blocked

    # Relationship with the Service model
    service_type = db.relationship('Service', backref='professionals', lazy=True)



# Service Model
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.String(50), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    
    def __str__(self):
        return f"Service(id={self.id}, name={self.name}, price={self.price})"
    
# Service Request Model
class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_of_request = db.Column(db.DateTime, default=func.now())
    date_of_completion = db.Column(db.DateTime, nullable=True)
    service_status = db.Column(db.String(50), default='Requested')  # Requested, Assigned, Closed
    remarks = db.Column(db.String(255), nullable=True)

    # Correct foreign key for service_id
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.String, db.ForeignKey('customer.id'), nullable=False)
    professional_id = db.Column(db.String, db.ForeignKey('service_professional.id'), nullable=True)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=True)

    # Relationship definitions
    service = db.relationship('Service', backref='requests', lazy=True)  # Correctly linked to Service
    customer = db.relationship('Customer', backref='service_requests', lazy=True)
    professional = db.relationship('Service_Professional', backref='service_requests', lazy=True)
    review = db.relationship('Review', backref='service_request', lazy=True)

    def __str__(self):
        return f"ServiceRequest(id={self.id}, service_status={self.service_status}, customer_id={self.customer_id})"


# Review Model (for service professionals)
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # Rating out of 5
    comment = db.Column(db.String(255), nullable=True)
    
    # Foreign keys to link review with customer and service professional
    customer_id = db.Column(db.String, db.ForeignKey('customer.id'), nullable=False)
    professional_id = db.Column(db.String, db.ForeignKey('service_professional.id'), nullable=False)

    # Relationship definitions
    customer = db.relationship('Customer', backref='reviews', lazy=True)
    professional = db.relationship('Service_Professional', backref='reviews', lazy=True)

    def __str__(self):
        return f"Review(id={self.id}, rating={self.rating}, customer_id={self.customer_id})"

