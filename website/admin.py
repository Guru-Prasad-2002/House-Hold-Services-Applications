from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from .models import Admin, Service, Service_Professional, Customer, Review, ServiceRequest
from . import db
from sqlalchemy.sql import func

# Blueprint has a bunch of routes/urls inside it

admin = Blueprint('admin', __name__,template_folder='templates_admin',
    static_folder='static')

@admin.route('/')
@login_required
def home():
    if isinstance(current_user, Admin):
        return render_template("admin.html")
    return render_template("no_permission.html")

@admin.route('/service_management')
@login_required
def service_management():
    if isinstance(current_user, Admin):
        services = Service.query.all()
        return render_template("admin_services.html", services=services)
    return render_template("no_permission.html")


@admin.route('/service_management/add', methods=['POST'])
@login_required
def add_service():
    if isinstance(current_user, Admin):
        name = request.form.get('name')
        price = request.form.get('price')
        time_required = request.form.get('time_required')
        description = request.form.get('description')
        
        new_service = Service(name=name, price=price, time_required=time_required, description=description)
        
        try:
            db.session.add(new_service)
            db.session.commit()
            flash('Service added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error adding service!', 'danger')

        return redirect(url_for('admin.service_management'))
    return render_template("no_permission.html")

@admin.route('/service_management/edit/<int:id>', methods=['POST'])
@login_required
def edit_service(id):
    if isinstance(current_user, Admin):
        service = Service.query.get(id)
        service.name = request.form.get('name')
        service.price = request.form.get('price')
        service.time_required = request.form.get('time_required')
        service.description = request.form.get('description')

        try:
            db.session.commit()
            flash('Service updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating service!', 'danger')

        return redirect(url_for('admin.service_management'))
    return render_template("no_permission.html")

@admin.route('/service_management/delete/<int:id>', methods=['POST'])
@login_required
def delete_service(id):
    if isinstance(current_user, Admin):
        service = Service.query.get(id)
        if service.professionals:  # `professionals` is the backref relationship
            flash('Cannot delete service. There are professionals associated with this service.', 'danger')
            return redirect(url_for('admin.service_management'))
        try:
            db.session.delete(service)
            db.session.commit()
            flash('Service deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error deleting service!', 'danger')
        return redirect(url_for('admin.service_management'))
    return render_template("no_permission.html")

@admin.route('/service_professional_verification', methods=['GET', 'POST'])
@login_required
def service_professional_verification():
    if not isinstance(current_user, Admin):
        return render_template("no_permission.html")
    
    # Fetch all service professionals with status 'Pending'
    pending_sps = Service_Professional.query.filter_by(status='Pending').all()

    if request.method == 'POST':
        sp_id = request.form.get('sp_id')
        sp = Service_Professional.query.get(sp_id)
        if sp and sp.status == 'Pending':
            sp.status = 'Approved'
            db.session.commit()
            flash("Service Professional verified successfully", "success")
        return redirect(url_for('admin.service_professional_verification'))

    return render_template('admin_sp_verification.html', pending_sps=pending_sps)


@admin.route('/service_professional_management', methods=['GET', 'POST'])
@login_required
def service_professional_management():
    if not isinstance(current_user, Admin):
        return render_template("no_permission.html")

    # Query service professionals with their average ratings
    approved_sps = db.session.query(
        Service_Professional,
        func.avg(Review.rating).label('average_rating')
    ).outerjoin(Review, Review.professional_id == Service_Professional.id)\
     .filter(Service_Professional.status == 'Approved')\
     .group_by(Service_Professional.id).all()

    blocked_sps = db.session.query(
        Service_Professional,
        func.avg(Review.rating).label('average_rating')
    ).outerjoin(Review, Review.professional_id == Service_Professional.id)\
     .filter(Service_Professional.status == 'Blocked')\
     .group_by(Service_Professional.id).all()

    if request.method == 'POST':
        sp_id = request.form.get('sp_id')
        action = request.form.get('action')
        sp = Service_Professional.query.get(sp_id)
        
        if sp:
            if action == 'block':
                sp.status = 'Blocked'
            elif action == 'unblock':
                sp.status = 'Approved'
            db.session.commit()
            flash("Service Professional status updated", "success")
        return redirect(url_for('admin.service_professional_management'))

    return render_template('admin_sp_mgmt.html', approved_sps=approved_sps, blocked_sps=blocked_sps)

@admin.route('/customer_management', methods=['GET', 'POST'])
@login_required
def customer_management():
    if not isinstance(current_user, Admin):
        return render_template("no_permission.html")

    # Separate blocked and unblocked customers
    unblocked_customers = Customer.query.filter_by(status='UnBlocked').all()
    blocked_customers = Customer.query.filter_by(status='Blocked').all()

    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        action = request.form.get('action')
        customer = Customer.query.get(customer_id)
        
        if customer:
            if action == 'block':
                customer.status = 'Blocked'
            elif action == 'unblock':
                customer.status = 'UnBlocked'
            db.session.commit()
            flash("Customer status updated", "success")
        return redirect(url_for('admin.customer_management'))

    return render_template('admin_customer_mgmt.html', unblocked_customers=unblocked_customers, blocked_customers=blocked_customers)

@admin.route('/service_requests', methods=['GET'])
@login_required
def service_requests():
    if not isinstance(current_user, Admin):
        return render_template("no_permission.html")
    
    # Get the filter from query parameters; default to 'All'
    filter_status = request.args.get('status', 'All')

    # Query Service Requests based on the selected filter
    if filter_status == 'All':
        service_requests = ServiceRequest.query.all()
    else:
        service_requests = ServiceRequest.query.filter_by(service_status=filter_status).all()

    return render_template(
        'admin_service_requests.html',
        service_requests=service_requests,
        filter_status=filter_status
    )