from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import Professional, User, Service, Notification
from utils import admin_required, professional_required
from flask import request, current_app
from werkzeug.utils import secure_filename
import os
import uuid
from extensions import cache
class ProfessionalResource(Resource):
    def get(self, professional_id):
        professional = Professional.query.get_or_404(professional_id)
        professional_data = professional.to_dict()

        return {"professional": professional_data}, 200
    
    @jwt_required()
    def put(self, professional_id):
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)

        professional = Professional.query.get_or_404(professional_id)
        if user.id != professional.user_id and user.role != 'admin':
            return {"message": "Not authorized to update this profile"}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('bio', type=str)
        parser.add_argument('years_experience', type=int)
        parser.add_argument('phone', type=str)
        parser.add_argument('name', type=str)

        # parser.add_argument('service_id', type=int)
        
        data = parser.parse_args()

        if data['bio'] is not None:
            professional.bio = data['bio']

        if data['years_experience'] is not None:
            professional.years_experience = data['years_experience']
        
        if data['phone'] is not None:
            professional.user.phone = data['phone']
        
        if data['name'] is not None:
            professional.user.name = data['name']

        # 
        # if data['service_id'] is not None:
        #     service = Service.query.get(data['service_id'])
        #     if service:
        #         professional.service_id = service.id
        #     else:
        #         return {"message": "Service not found"}, 404

        
        try:
            professional.save_to_db()
            cache.clear()
            return {"message": "Professional updated successfully", "professional": professional.to_dict()}, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
    @jwt_required()
    @admin_required
    def delete(self, professional_id):
        """Delete a professional (admin only)"""
        professional = Professional.query.get_or_404(professional_id)
        
        try:
            
            user = professional.user
            professional.delete_from_db()
            user.delete_from_db()

            cache.clear()
            
            return {"message": "Professional deleted successfully"}, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
class ProfessionalListResource(Resource):

    def get(self):

        service_id = request.args.get('service_id', type=int)
        verified_only = request.args.get('verified_only', 'true').lower() == 'true'
        rating_min = request.args.get('rating_min', type=float)
        
        # Build query
        query = Professional.query
        
        if service_id:
            query = query.filter_by(service_id=service_id)
            
        if verified_only:
            query = query.filter_by(verification_status='approved')
            
        # Get professionals
        professionals = query.all()
        
        # Filter by rating if needed
        if rating_min:
            professionals = [p for p in professionals if p.get_average_rating() >= rating_min]
            
        result = [professional.to_dict() for professional in professionals]
        
        return {"professionals": result}, 200


class ProfessionalVerificationResource(Resource):

    @jwt_required()
    @admin_required
    def post(self,professional_id):
        parser = reqparse.RequestParser()
        parser.add_argument('action', type=str, required=True, help="Action cannot be blank")
        parser.add_argument('message', type=str)

        data = parser.parse_args()

        professional = Professional.query.get_or_404(professional_id)

        if data['action'] not in ['approve', 'reject']:
            return {"message": "Action must be either 'approve' or 'reject'"}, 400
        
        if data['action'] == 'approve':
            professional.verification_status = 'approved'
            message = data['message'] or "Your profile has been approved. You can now accept service requests."

        elif data['action'] == 'reject':
            professional.verification_status = 'rejected'
            message = data['message'] or "Your profile verification has been rejected. Please contact admin for details."
            
        try:
            professional.save_to_db()
            
            cache.clear()
            notification = Notification(
                user_id = professional.user_id,
                type='verification',
                message=message
            )
            notification.save_to_db()

            return {
                "message": f"Professional {data['action']}d successfully",
                "professional": professional.to_dict()
            }, 200
        
        except Exception as e:
            print(f"Error: {str(e)}")
            return {"message": f"An error occurred: {str(e)}"}, 500
        
    @jwt_required()
    @professional_required
    def put(self, professional_id):
        current_user_id = get_jwt_identity()
        professional = Professional.query.get_or_404(professional_id)
        
        if int(professional.user_id) != int(current_user_id):
            print("Not authorized to update this profile")
            return {"message": "Not authorized to update this profile"}, 403

        if 'document' not in request.files:
            return {"message": "No document part in the request"}, 400
        
        file = request.files['document']

        if file.filename == '':
            return {"message": "No selected file"}, 400
        
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"

        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', unique_filename)
        file.save(file_path)

        if professional.documents_url:
            professional.documents_url += f",{unique_filename}"
        else:
            professional.documents_url = unique_filename

        if professional.verification_status != 'rejected':
            professional.verification_status = 'pending'

        try:
            professional.save_to_db()

            admin_user = User.query.filter_by(role='admin').first()
            notification = Notification(
                user_id=admin_user.id,
                type='document_upload',
                message=f"Professional {professional.user.name} has uploaded verification documents."
            )
            notification.save_to_db()

            cache.clear()
            return {
                "message": "Document uploaded successfully",
                "professional": professional.to_dict()
            }, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500