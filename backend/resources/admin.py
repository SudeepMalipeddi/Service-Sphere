from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from utils import admin_required
from models import *
from sqlalchemy import func,desc
import datetime

class AdminDashboardResource(Resource):

    @jwt_required()
    @admin_required
    def get(self):
        total_customers = Customer.query.count()
        total_professionals = Professional.query.count()
        total_services = Service.query.count()
        total_service_requests = ServiceRequest.query.count()

        active_customers = Customer.query.join(User).filter(User.is_active==True).count()
        verified_professionals = Professional.query.filter_by(verification_status='approved').count()


        today = datetime.datetime.today()
        last_week = today - datetime.timedelta(days=7)

        new_customers = Customer.query.filter(Customer.registered_on >= last_week).count()
        new_professionals = Professional.query.filter(Professional.registered_on >= last_week).count()
        new_requests = ServiceRequest.query.filter(ServiceRequest.request_date >= last_week).count()


        status_counts = (
            ServiceRequest.query
            .with_entities(ServiceRequest.status, func.count().label('count'))
            .group_by(ServiceRequest.status)
            .all()
        )

        status_counts_dict = {status: count for status, count in status_counts}

        pending_verifications = Professional.query.filter_by(verification_status='pending').count()

        return {
            "total_counts": {
                "customers": total_customers,
                "professionals": total_professionals,
                "services": total_services,
                "service_requests": total_service_requests
            },
            "active_counts": {
                "customers": active_customers,
                "professionals": verified_professionals,
                "services": total_services,
            },
            "recent_activity": {
                "new_customers": new_customers,
                "new_professionals": new_professionals,
                "new_requests": new_requests
            },
            "request_status":status_counts_dict,
            "pending_verifications": pending_verifications
        }
    

class AdminProfessionalsResource(Resource):

    @jwt_required()
    @admin_required
    def get(self):

        status = request.args.get('status')
        service_id = request.args.get('service_id', type=int)
        verification_status = request.args.get('verification_status')

        # query = Professional.query
        query = db.session.query(Professional).join(User)

        if status:
            is_active = status.lower() == 'active'
            query = query.filter(User.is_active == is_active)
            # query = query.join(User).filter(User.is_active == (status.lower() == 'active'))
        
        if service_id is not None:
            query = query.filter(Professional.service_id == service_id)

        if verification_status:
            query = query.filter(Professional.verification_status==verification_status)

        
        professionals = query.all()

        return {"professionals": [prof.to_dict() for prof in professionals]}, 200
    
    @jwt_required()
    @admin_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('professional_id',type=int,required=True,help="Professional ID is required")
        parser.add_argument('status', type=str, required=True, help="Status is required")

        data = parser.parse_args()

        professional = Professional.query.get_or_404(data['professional_id'])

        if data['status'] not in ['active','inactive']:
            return {"message": "Status must be either 'active' or 'inactive'"}, 400
        
        professional.user.is_active = (data['status'] == 'active')

        try:
            professional.user.save_to_db()

            notification = Notification(
                user_id=professional.user_id,
                type='account_status',
                message=f"Your account has been {'activated' if professional.user.is_active else 'deactivated'} by an administrator.",
            )

            notification.save_to_db()

            return {
                "message": f"Professional account has been {'activated' if professional.user.is_active else 'deactivated'}",
                "professional": professional.to_dict()
            }, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        

class AdminCustomersResource(Resource):

    @jwt_required()
    @admin_required
    def get(self):

        status = request.args.get('status')
        search = request.args.get('search')

        query = Customer.query

        if status:
            query = query.join(User).filter(User.is_active == (status.lower() == 'active'))

        if search:
            query = query.join(User).filter(
                (User.name.ilike(f'%{search}%')) |
                (User.email.ilike(f'%{search}%')) |
                (Customer.pincode.ilike(f'%{search}%'))
            )

        customers = query.all()

        return {"customers": [cust.to_dict() for cust in customers]}, 200
    
    @jwt_required()
    @admin_required
    def put(self):

        parser = reqparse.RequestParser()
        parser.add_argument('customer_id', type=int, required=True, help="Customer ID is required")
        parser.add_argument('status', type=str, required=True, help="Status is required")


        data = parser.parse_args()

        customer = Customer.query.get_or_404(data['customer_id'])

        if data['status'] not in ['active','inactive']:
            return {"message": "Status must be either 'active' or 'inactive'"}, 400
        
        customer.user.is_active = (data['status'] == 'active')

        try:
            customer.user.save_to_db()

            notification = Notification(
                user_id=customer.user_id,
                type='account_status',
                message=f"Your account has been {'activated' if customer.user.is_active else 'deactivated'} by an administrator.",
            )

            notification.save_to_db()

            return {
                "message": f"Customer account has been {'activated' if customer.user.is_active else 'deactivated'}",
                "customer": customer.to_dict()
            }, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500