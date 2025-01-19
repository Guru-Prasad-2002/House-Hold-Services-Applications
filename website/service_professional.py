from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Service_Professional, ServiceRequest
from . import db
from flask_login import login_required, current_user

# Blueprint has a bunch of routes/urls inside it

service_professional = Blueprint('service_professional', __name__,template_folder='templates_service_professionals',
    static_folder='static')

@service_professional.route('/')
@login_required
def home():
    if isinstance(current_user, Service_Professional):
        if current_user.status == 'Approved':
            # Fetch new and assigned service requests for the current professional
            new_requests = ServiceRequest.query.filter_by(
                professional_id=current_user.id, service_status='Requested'
            ).all()

            ongoing_requests = ServiceRequest.query.filter_by(
                professional_id=current_user.id, service_status='Assigned'
            ).all()

            return render_template(
                "service_professionals.html",
                new_requests=new_requests,
                ongoing_requests=ongoing_requests,
            )
        elif current_user.status == 'Pending':
            return render_template("service_professional_pending.html")
        elif current_user.status == 'Blocked':
            return render_template("service_professional_blocked.html")
    return render_template("no_permission.html")


@service_professional.route('/accept_reject_request', methods=['POST'])
@login_required
def accept_reject_request():
    if isinstance(current_user, Service_Professional) and current_user.status == 'Approved':
        sr_id = request.form.get('sr_id')
        action = request.form.get('action')  # Either 'accept' or 'reject'

        sr = ServiceRequest.query.get(sr_id)

        if sr and sr.professional_id == current_user.id:
            if action == 'accept':
                sr.service_status = 'Assigned'
                flash('Service Request Accepted!', 'success')
            elif action == 'reject':
                sr.service_status = 'Rejected'
                flash('Service Request Rejected!', 'warning')
            db.session.commit()

        return redirect(url_for('service_professional.home'))
    return render_template("no_permission.html")


@service_professional.route('/service_history')
@login_required
def service_history():
    if isinstance(current_user, Service_Professional) and current_user.status == 'Approved':
        closed_requests = ServiceRequest.query.filter_by(
            professional_id=current_user.id, service_status='Closed'
        ).all()

        return render_template(
            "service_professional_history.html", closed_requests=closed_requests
        )
    return render_template("no_permission.html")
