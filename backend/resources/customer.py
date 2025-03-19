from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Customer,User,ServiceRequest
from utils import admin_required
from flask import request


class CustomerResource(Resource):

    @jwt_required()
    
    def get(self, customer_id):
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        customer = Customer.query.get_or_404(customer_id)

        if user.id != customer.user_id and user.role != 'admin' :
            return {"message": "Not authorized to view this profile"}, 403

        total_requests = ServiceRequest.query.filter_by(customer_id=customer_id).count()
        completed_requests = ServiceRequest.query.filter_by(
            customer_id=customer_id, status='closed'
        ).count()

        customer_data = customer.to_dict()
        customer_data['total_requests'] = total_requests
        customer_data['completed_requests'] = completed_requests

        return {"customer": customer_data}, 200
    
    @jwt_required()
    def put(self,customer_id):
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        
        
        customer = Customer.query.get_or_404(customer_id)
        if user.id != customer.user_id and user.role != 'admin':
            return {"message": "Not authorized to update this profile"}, 403
        

        parser = reqparse.RequestParser()
        parser.add_argument('address', type=str)
        parser.add_argument('pincode', type=str)
        parser.add_argument('phone', type=str)
        parser.add_argument('name', type=str)
        
        data = parser.parse_args()
        
        
        if data['address'] is not None:
            customer.address = data['address']
        if data['pincode'] is not None:
            customer.pincode = data['pincode']
            
        
        if data['phone'] is not None:
            customer.user.phone = data['phone']
        if data['name'] is not None:
            customer.user.name = data['name']
            
        try:
            customer.save_to_db()
            customer.user.save_to_db()
            return {"message": "Profile updated successfully", "customer": customer.to_dict()}, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
    @jwt_required()
    @admin_required
    def delete(self,customer_id):
        customer = Customer.query.get_or_404(customer_id)

        try:
            user = customer.user
            customer.delete_from_db()
            user.delete_from_db()

            return {"message": "Customer deleted successfully"}, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
class CustomerListResource(Resource):
    
    @jwt_required()
    @admin_required
    def get(self):
        search_query = request.args.get('q', '')
        
        query = Customer.query.join(User)
        
        if search_query:
            query = query.filter(
                (User.name.ilike(f'%{search_query}%')) |
                (User.email.ilike(f'%{search_query}%')) |
                (Customer.pincode.ilike(f'%{search_query}%'))
            )
            
        
        customers = query.all()
        
        result = []
        for customer in customers:
            total_requests = ServiceRequest.query.filter_by(customer_id=customer.id).count()
            completed_requests = ServiceRequest.query.filter_by(
                customer_id=customer.id, 
                status='closed'
            ).count()
            
            customer_data = customer.to_dict()
            customer_data['total_requests'] = total_requests
            customer_data['completed_requests'] = completed_requests
            
            result.append(customer_data)
        
        return {"customers": result}, 200
