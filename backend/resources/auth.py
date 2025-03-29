from flask_restful import Resource,reqparse
from flask_jwt_extended import create_access_token,create_refresh_token,jwt_required,get_jwt_identity,get_jwt
from flask import current_app, request
from models import User,Customer,Professional,Service
import re

class UserRegister(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help="Email cannot be blank")
        parser.add_argument('password', type=str, required=True, help="Password cannot be blank")
        parser.add_argument('name', type=str, required=True, help="Name cannot be blank")
        parser.add_argument('phone', type=str)
        parser.add_argument('role', type=str, required=True, help="Role cannot be blank")
        parser.add_argument('address', type=str)
        parser.add_argument('pincode', type=str)
        parser.add_argument('service_id', type=int)
        parser.add_argument('years_experience', type=int)
        parser.add_argument('bio', type=str)
        
        data = parser.parse_args()

        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            return {"message": "Invalid email format"}, 400
        
        if User.query.filter_by(email=data['email']).first():
            return {"message": "A user with that email already exists"}, 400
        
        if data['role'] not in ['customer','professional']:
            return {"message": "Role must be either 'customer' or 'professional'"}, 400
        
        user = User(
            email=data['email'],
            name=data['name'],
            role=data['role'],
            phone=data['phone'] if data['phone'] else None,
            is_active=True
        )
        user.set_password(data['password'])
        
        try:
            user.save_to_db()

            if data['role'] == 'customer':
                customer = Customer(
                    user_id = user.id,
                    address = data['address'] if data['address'] else None,
                    pincode = data['pincode'] if data['pincode'] else None
                )
                customer.save_to_db()

            elif data['role'] == 'professional':
                if not data['service_id']:
                    user.delete_from_db()
                    return {"message": "Service ID is required for professionals"}, 400
                

                service = Service.query.get(data['service_id'])
                if not service:
                    user.delete_from_db()
                    return {"message": "Service not found"}, 404
                
                professional = Professional(
                    user_id = user.id,
                    service_id = data['service_id'],
                    years_experience = data['years_experience'] if data['years_experience'] else 0,
                    bio = data['bio'] if data['bio'] else None,
                    verification_status = 'pending'
                )

                professional.save_to_db()
            
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            return {
                "message": "User created successfully",
                "user": user.to_dict(),
                "access_token": access_token,
                "refresh_token": refresh_token
            },201
        
        except Exception as e:
            user.delete_from_db()
            return {"message": f"An error occurred: {str(e)}"}, 500
        

class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help="Email cannot be blank")
        parser.add_argument('password', type=str, required=True, help="Password cannot be blank")
        
        data = parser.parse_args()

        user = User.query.filter_by(email=data['email']).first()
        
        if user and user.check_password(data['password']):
            if not user.is_active:
                return {"message": "Account is inactive. Please contact admin."}, 401
                
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            customer_id = user.customer.id if user.customer else None
            professional_id = user.professional.id if user.professional else None
            

            return {
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role,
                    "customer_id": customer_id,  
                    "professional_id": professional_id,
                    "is_active": user.is_active,
                },
                "access_token": access_token,
                "refresh_token": refresh_token
            }, 200
            
        return {"message": "Invalid credentials"}, 401
    

class UserRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or not user.is_active:
            return {"message": "User not found or inactive"}, 401
            
        access_token = create_access_token(identity=current_user_id)
        
        return {
            "message": "Token refreshed",
            "access_token": access_token
        }, 200
    

class UserLogout(Resource):
    @jwt_required()
    def post(self):
        token = request.headers.get("Authorization")
        if not token:
            return {"error": "Missing Authorization Header"}, 401

        return {"message": "Logged out successfully"}, 200