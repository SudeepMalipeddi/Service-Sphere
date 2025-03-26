from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required,get_jwt_identity
from models import Service,Professional
from utils import admin_required
from sqlalchemy import or_, and_
import json
from flask import request

class ServiceResource(Resource):

    def get(self,service_id):

        service = int(service_id)
        service = Service.query.get_or_404(service)

        service_data = {
            "service": service.to_dict()
        }

        return service_data,200
    
    @jwt_required()
    @admin_required
    def put(self,service_id):
        parser = reqparse.RequestParser()
        
        parser.add_argument('name', type=str)
        parser.add_argument('base_price', type=float)
        parser.add_argument('estimated_time', type=int)
        parser.add_argument('description', type=str)
        parser.add_argument('is_active', type=bool)
        
        service = Service.query.get_or_404(service_id)
        data = parser.parse_args()

        for key, value in data.items():
            if value is not None:
                setattr(service, key, value)

        try:
            service.save_to_db()

            return {"message": "Service updated successfully", "service": service.to_dict()}, 200
        
        except Exception as e:
            return {"message": f"An error occurred : {str(e)}"}, 500
        

    
    @jwt_required()
    @admin_required
    def delete(self,service_id):
        service = Service.query.get_or_404(service_id)
        professionals = Professional.query.filter_by(service_id=service_id).all()
        if professionals:
            return {"message": "Cannot delete service. There are professionals associated with this service."}, 400
        
        try:
            service.delete_from_db()
            return {"message": "Service deleted successfully"}, 200
        
        except Exception as e:
            return {"message": f"An error occurred : {str(e)}"}, 500
        

class ServiceListResource(Resource):

    def get(self):
        search_query = request.args.get('q','')
        show_inactive = request.args.get('show_inactive','false').lower() == 'true'
        show_unavailable = request.args.get('show_unavailable','false').lower() == 'true'
        
        query = Service.query

        if not show_inactive:
            query = query.filter_by(is_active=True)

        if search_query:
            query = query.filter(or_(
                Service.name.ilike(f'%{search_query}%'),
                Service.description.ilike(f'%{search_query}%')
            ))

        services = query.all()
        
        result = []
        for service in services:
            service_dict = service.to_dict()
            
            if show_unavailable or service.has_verified_professionals():
                result.append(service_dict)

        return {"services": result}, 200
    
    @jwt_required()
    @admin_required
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help="Name is required")
        parser.add_argument('base_price', type=float, required=True, help="Base price is required")
        parser.add_argument('estimated_time', type=int, required=True, help="Estimated time in mins is required")
        parser.add_argument('description', type=str)
        parser.add_argument('is_active', type=bool, default=True)

        data = parser.parse_args()

        if Service.query.filter_by(name=data['name']).first():
            return {"message": "Service with this name already exists"}, 400
        
        service = Service(
            name=data['name'],
            base_price=data['base_price'],
            estimated_time=data['estimated_time'],
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )

        try:
            service.save_to_db()
            return {"message": "Service created successfully", "service": service.to_dict()}, 201   
        except Exception as e:
            return {"message": f"An error occurred : {str(e)}"}, 500
