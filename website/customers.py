from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Customer, ServiceRequest, Service_Professional, Review, Service
from . import db
from flask_login import login_required, current_user
from sqlalchemy.sql import func

# Blueprint has a bunch of routes/urls inside it
customers = Blueprint('customers', __name__, template_folder='templates_customers',
                    static_folder='static')

@customers.route('/')
@login_required
def home():
    if isinstance(current_user, Customer):
        if current_user.status == 'UnBlocked':
            # Fetch "Requested" and "Assigned" service requests
            sr_made = ServiceRequest.query.filter_by(service_status='Requested', customer_id=current_user.id).all()
            sr_assigned = ServiceRequest.query.filter_by(service_status='Assigned', customer_id=current_user.id).all()

            return render_template("customers.html", customer=current_user, sr_made=sr_made, sr_assigned=sr_assigned)
        elif current_user.status == 'Blocked':
            return render_template("customer_blocked.html")
    return render_template("no_permission.html")

@customers.route('/service_requests_made', methods=['GET', 'POST'])
@login_required
def service_requests_made():
    if isinstance(current_user, Customer):
        if current_user.status == 'UnBlocked':
            # Fetch all service requests in the 'Requested' state for the customer
            sr_made = ServiceRequest.query.filter_by(
                service_status='Requested', customer_id=current_user.id
            ).all()

            if request.method == 'POST':
                action = request.form.get('action')

                if action == 'create':
                    professional_id = request.form.get('professional_id')
                    remarks = request.form.get('remarks')
                    service_id = Service_Professional.query.get(professional_id).service_type_id
                    # print("Service_ID is", service_id)

                    new_service_request = ServiceRequest(
                        service_id=service_id,
                        customer_id=current_user.id,
                        professional_id=professional_id,
                        service_status='Requested',
                        remarks=remarks,
                    )
                    db.session.add(new_service_request)
                    db.session.commit()
                    flash('Service Request Created!', 'success')

                elif action == 'edit':
                    sr_id = request.form.get('sr_id')
                    remarks = request.form.get('remarks')
                    sr = ServiceRequest.query.get(sr_id)

                    if sr and sr.customer_id == current_user.id:
                        sr.remarks = remarks
                        db.session.commit()
                        flash('Service Request Edited!', 'success')

                elif action == 'delete':
                    sr_id = request.form.get('sr_id')
                    sr = ServiceRequest.query.get(sr_id)

                    if sr and sr.customer_id == current_user.id:
                        db.session.delete(sr)
                        db.session.commit()
                        flash('Service Request Deleted!', 'success')

                # return redirect(url_for('customers.home'))

            # return render_template("customer_sr_made.html", sr_made=sr_made)
            return redirect(url_for('customers.home'))
        else:
            return render_template("customer_blocked.html")
    return render_template("no_permission.html")

@customers.route('/service_requests_assigned', methods=['GET', 'POST'])
@login_required
def service_requests_assigned():
    if isinstance(current_user, Customer):
        if current_user.status == 'UnBlocked':
            # Fetch all service requests in the 'Assigned' state for the customer
            sr_assigned = ServiceRequest.query.filter_by(
                service_status='Assigned', customer_id=current_user.id
            ).all()

            if request.method == 'POST':
                sr_id = request.form.get('sr_id')
                rating = request.form.get('rating')
                comment = request.form.get('comment')

                sr = ServiceRequest.query.get(sr_id)

                if sr and sr.customer_id == current_user.id:
                    sr.service_status = 'Closed'
                    sr.date_of_completion = func.now()
                    db.session.commit()

                    # Add a review for the professional
                    review = Review(
                        rating=rating,
                        comment=comment,
                        customer_id=current_user.id,
                        professional_id=sr.professional_id,
                    )
                    db.session.add(review)
                    db.session.commit()

                    sr.review_id = review.id
                    db.session.commit()
                    flash('Service Request Closed and Review Submitted!', 'success')

            return redirect(url_for('customers.home'))
        else:
            return render_template("customer_blocked.html")
    return render_template("no_permission.html")



@customers.route('/new_service_request', methods=['GET', 'POST'])
@login_required
def new_service_request():
    if isinstance(current_user, Customer):
        if current_user.status == 'UnBlocked':
            # Get all services (for dropdown)
            service_types = Service.query.all()

            # Retrieve the selected filters from the form
            selected_service_type_id = request.form.get('service_type', type=int)
            location_filter = request.form.get('location', type=str)
            pin_code_filter = request.form.get('pin_code', type=str)

            # Query professionals based on selected filters
            query = Service_Professional.query.filter_by(status='Approved')

            if selected_service_type_id:
                query = query.filter_by(service_type_id=selected_service_type_id)
            if location_filter:
                query = query.filter(Service_Professional.location.ilike(f"%{location_filter}%"))
            if pin_code_filter:
                query = query.filter_by(pin_code=pin_code_filter)

            professionals = query.all()
            for professional in professionals:
                # Calculate the average rating from the reviews
                avg_rating = db.session.query(db.func.avg(Review.rating)).filter(Review.professional_id == professional.id).scalar()
                professional.avg_rating = avg_rating if avg_rating is not None else 0


            return render_template(
                "new_service_request.html",
                professionals=professionals,
                service_types=service_types,
                selected_service_type=selected_service_type_id,
                location_filter=location_filter,
                pin_code_filter=pin_code_filter
            )
        else:
            return render_template("customer_blocked.html")
    return render_template("no_permission.html")

@customers.route('/service_requests_history')
@login_required
def service_requests_history():
    if isinstance(current_user, Customer):
        if current_user.status == 'UnBlocked':
            # Fetch closed and rejected service requests for the current customer
            sr_closed = ServiceRequest.query.filter_by(service_status='Closed', customer_id=current_user.id).all()

            sr_rejected = ServiceRequest.query.filter_by(
                service_status='Rejected', customer_id=current_user.id
            ).all()

            return render_template(
                "customer_sr_history.html", sr_closed=sr_closed, sr_rejected=sr_rejected
            )
        else:
            return render_template("customer_blocked.html")
    return render_template("no_permission.html")