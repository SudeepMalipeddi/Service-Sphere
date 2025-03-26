from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import ServiceRequest,Customer,Professional,Service,User,RejectedServiceRequest,Notification
from utils import customer_required,role_required
from flask import request
from datetime import datetime,timezone

class ServiceRequestResource(Resource):
    
    @jwt_required()
    def get(self,request_id):

        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        service_request = ServiceRequest.query.get(request_id)

        if user.role == 'customer':
            customer = Customer.query.filter_by(user_id=user.id).first()
            if not customer or service_request.customer_id != customer.id:
                return {"message": "Not authorized to view this service request"}, 403
        
        elif user.role == 'professional':
            professional = Professional.query.filter_by(user_id=user.id).first()

            if not professional or (
                service_request.professional_id != professional.id and
                not ( service_request.status == 'requested' and service_request.service_id == professional.service_id)
            ):
                return {"message": "Not authorized to view this service request"}, 403
            
        return {"service_request": service_request.to_dict()}, 200
    

    @jwt_required()
    @customer_required
    def put(self, request_id):

        current_user_id = get_jwt_identity()
        customer = Customer.query.filter_by(user_id=current_user_id).first_or_404()
        
        service_request = ServiceRequest.query.get_or_404(request_id)

        if service_request.customer_id != customer.id:
            return {"message": "Not authorized to update this service request"}, 403
        
        if service_request.status in ['closed', 'cancelled']:
            return {"message": "Cannot update a closed  or cancelled service request"}, 400
        
        if service_request.status == 'assigned':
            return {"message": "Cannot update an assigned service request"}, 400
        
        parser = reqparse.RequestParser()
        parser.add_argument('scheduled_date', type=str)
        parser.add_argument('remarks', type=str)

        data = parser.parse_args()

        if data['scheduled_date'] is not None:
            try:
                scheduled_date = datetime.fromisoformat(data['scheduled_date'].replace('Z', '+00:00'))
                service_request.scheduled_date = scheduled_date
            except ValueError:
                return {"message": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}, 400
            
        if data['remarks'] is not None:
            service_request.remarks = data['remarks']

        try:
            service_request.save_to_db()

            if service_request.professional_id:
                notification = Notification(
                    user_id=service_request.professional.user_id,
                    type='request_updated',
                    message=f"Service request # {service_request.id} has been updated by the customer."
                )
                notification.save_to_db()

            return {
                "message": "Service request updated successfully", 
                "service_request": service_request.to_dict()
            }, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
    @jwt_required()
    @customer_required
    def delete(self, request_id):
        """Cancel a service request (customer only)"""
        current_user_id = get_jwt_identity()
        customer = Customer.query.filter_by(user_id=current_user_id).first_or_404()
        
        service_request = ServiceRequest.query.get_or_404(request_id)
        
        
        if service_request.customer_id != customer.id:
            return {"message": "Not authorized to cancel this service request"}, 403
        
        
        if service_request.professional_id:
            return {"message": "Cannot cancel a service request with an assigned professional"}, 400

        
        if service_request.status in ['closed', 'cancelled']:
            return {"message": "Cannot cancel a closed or already cancelled service request"}, 400
        

        service_request.status = 'cancelled'
        try:
            service_request.save_to_db()
            return {"message": "Service request cancelled successfully"}, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        

class ServiceRequestListResource(Resource):

    @jwt_required()
    def get(self):

        current_user_id = get_jwt_identity()
        
        user = User.query.get_or_404(current_user_id)

        status = request.args.get('status')

        if user.role == 'customer':
            customer = Customer.query.filter_by(user_id=user.id).first_or_404()
            query = ServiceRequest.query.filter_by(customer_id=customer.id)

        elif user.role == 'professional':
            
            professional = Professional.query.filter_by(user_id=user.id).first_or_404()
            
            
            show_available = request.args.get('available', 'false').lower() == 'true'

            include_rejected = request.args.get('include_rejected', 'false').lower() == 'true'
        
            if show_available:
                query = ServiceRequest.query.filter(
                    ServiceRequest.service_id == professional.service_id,
                    ServiceRequest.status == 'requested',
                    ServiceRequest.professional_id.is_(None)
                )
                if not include_rejected:

                    rejected_requests = RejectedServiceRequest.query.filter_by(
                        professional_id=professional.id
                    ).with_entities(RejectedServiceRequest.service_request_id).all()
                    
                    rejected_ids = [req[0] for req in rejected_requests]

                    if rejected_ids:
                        query = query.filter(~ServiceRequest.id.in_(rejected_ids))
            else:
                query = ServiceRequest.query.filter_by(professional_id=professional.id)
                
        elif user.role == 'admin':
            
            query = ServiceRequest.query
            
            
            service_id = request.args.get('service_id', type=int)
            customer_id = request.args.get('customer_id', type=int)
            professional_id = request.args.get('professional_id', type=int)
            
            if service_id:
                query = query.filter_by(service_id=service_id)
            if customer_id:
                query = query.filter_by(customer_id=customer_id)
            if professional_id:
                query = query.filter_by(professional_id=professional_id)
        else:
            return {"message": "Invalid user role"}, 400
            
        
        if status:
            query = query.filter_by(status=status)
            
        
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        if date_from:
            try:
                date_from = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(ServiceRequest.request_date >= date_from)
            except ValueError:
                return {"message": "Invalid date_from format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}, 400
                
        if date_to:
            try:
                date_to = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(ServiceRequest.request_date <= date_to)
            except ValueError:
                return {"message": "Invalid date_to format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}, 400
        
        
        service_requests = query.order_by(ServiceRequest.request_date.desc()).all()
        
        return {
            "service_requests": [req.to_dict() for req in service_requests],
            "count": len(service_requests)
        }, 200

    @jwt_required()
    @customer_required
    def post(self):
        current_user_id = get_jwt_identity()
        customer = Customer.query.filter_by(user_id=current_user_id).first_or_404()
        
        parser = reqparse.RequestParser()
        parser.add_argument('service_id', type=int, required=True, help="Service ID is required")
        parser.add_argument('scheduled_date', type=str, required=True, help="Scheduled date is required")
        parser.add_argument('remarks', type=str)
        
        data = parser.parse_args()
        
        
        service = Service.query.get(data['service_id'])
        if not service:
            return {"message": "Service not found"}, 404
        if not service.is_active:
            return {"message": "This service is not currently active"}, 400
            
        
        try:
            scheduled_date = datetime.fromisoformat(data['scheduled_date'].replace('Z', '+00:00'))
            
            scheduled_date = scheduled_date.replace(tzinfo=timezone.utc)
        
            if scheduled_date <= datetime.now(timezone.utc):
                return {"message": "Scheduled date must be in the future"}, 400
        except ValueError:
            return {"message": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}, 400
            
        
        new_request = ServiceRequest(
            customer_id=customer.id,
            service_id=data['service_id'],
            professional_id=None,  
            request_date=datetime.utcnow(),
            scheduled_date=scheduled_date,
            status='requested',
            remarks=data.get('remarks', '')
        )
        
        try:
            new_request.save_to_db()
            
            
            professionals = Professional.query.filter_by(
                service_id=data['service_id'],
                verification_status='approved'
            ).all()
            
            for professional in professionals:
                notification = Notification(
                    user_id=professional.user_id,
                    type='new_request',
                    message=f"A new service request is available in your area."
                )
                notification.save_to_db()
            
            return {
                "message": "Service request created successfully", 
                "service_request": new_request.to_dict()
            }, 201
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

class ServiceRequestActionResource(Resource):

    @jwt_required()
    @role_required(['professional','customer'])
    def post(self,request_id):

        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        

        service_request = ServiceRequest.query.get(request_id)

        parser = reqparse.RequestParser()
        parser.add_argument('action', type=str, required=True, help="Action cannot be blank")
        parser.add_argument('reason', type=str)

        data = parser.parse_args()

        if user.role == 'professional':
            professional = Professional.query.filter_by(user_id=user.id).first_or_404()

            if data['action'] == 'accept':
                return self._handle_accept(service_request, professional)
            elif data['action'] == 'reject':
                return self._handle_reject(service_request, professional, data.get('reason', ''))
            elif data['action'] == 'complete':
                return self._handle_complete(service_request, professional)
            else:
                return {"message": "Invalid action for professional"}, 400
            
        elif user.role == 'customer':
            customer = Customer.query.filter_by(user_id=user.id).first_or_404()

            if service_request.customer_id != customer.id:
                return {"message": "Not authorized to take action on this service request"}, 403
            
            if data['action'] == 'close':
                return self._handle_close(service_request, customer)
            else:
                return {"message": "Invalid action for customer"}, 400
            
        return {"message": "Invalid user role"}, 400
    
    def _handle_accept(self, service_request, professional):

        if service_request.status != 'requested':
            return {"message": "This service request is no longer available"}, 400
        
        if service_request.service_id != professional.service_id:
            return {"message": "This service request does not match your service type"}, 400
        
        

        if professional.verification_status != 'approved':
            return {"message": "You must be verified to accept service requests"}, 403
        

        existing_rejection = RejectedServiceRequest.query.filter_by(
        service_request_id=service_request.id,
        professional_id=professional.id
        ).first()

        if existing_rejection:
            return {"message": "You cannot accept a request you have previously rejected"}, 400
        
        service_request.professional_id = professional.id
        service_request.status = 'assigned'

        try:
            service_request.save_to_db()

            notification = Notification(
                user_id=service_request.customer.user_id,
                type='request_accepted',
                message=f"Your service request has been accepted by {professional.user.name}."
            )
            notification.save_to_db()
            return {
                "message": "Service request accepted successfully", 
                "service_request": service_request.to_dict()
            }, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
    def _handle_reject(self, service_request, professional, reason):
        """Handle a professional rejecting a service request"""

        if service_request.service_id != professional.service_id:
            return {"message": "This service request does not match your service type"}, 400
        
        existing_rejection = RejectedServiceRequest.query.filter_by(
            service_request_id=service_request.id,
            professional_id=professional.id
        ).first()

        if existing_rejection:
            return {"message": "You have already rejected this service request"}, 400
        
        rejection = RejectedServiceRequest(
            service_request_id=service_request.id,
            professional_id=professional.id,
            reason=reason
        )

        try:
            rejection.save_to_db()

            if service_request.professional_id == professional.id:
                service_request.professional_id = None
                service_request.status = 'requested'
                service_request.save_to_db()
                
                notification = Notification(
                    user_id=service_request.customer.user_id,
                    type='request_rejected',
                    message=f"Your service request has been rejected by the professional."
                )
                notification.save_to_db()
            
            
            available_professionals = Professional.query.filter_by(
                service_id=service_request.service_id,
                verification_status='approved'
            ).all()
            
            
            total_professionals = len(available_professionals)
            
            if total_professionals > 0:
            
                rejections_count = RejectedServiceRequest.query.filter(
                    RejectedServiceRequest.service_request_id == service_request.id,
                    RejectedServiceRequest.professional_id.in_([p.id for p in available_professionals])
                ).count()
                
            
                if rejections_count >= total_professionals and service_request.status == 'requested':
                    service_request.status = 'cancelled'
                    service_request.save_to_db()
                    
            
                    notification = Notification(
                        user_id=service_request.customer.user_id,
                        type='request_cancelled',
                        message="Your service request has been cancelled as all available professionals have rejected it."
                    )
                    notification.save_to_db()
                    
                    return {"message": "Service request rejected and cancelled as all professionals have rejected it"}, 200
            
            return {"message": "Service request rejected successfully"}, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

    def _handle_complete(self, service_request, professional):

        if service_request.professional_id != professional.id:
            return {"message": "You are not assigned to this service request"}, 403
        
        if service_request.status != 'assigned':
            return {"message": "This service request cannot be completed. Invalid status."}, 400
        
        service_request.status = 'completed'
        service_request.completion_date = datetime.utcnow()

        try:
            service_request.save_to_db()
            
            # Notify customer
            notification = Notification(
                user_id=service_request.customer.user_id,
                type='request_completed',
                message=f"Your service request has been marked as completed by the professional. Please close it if you're satisfied."
            )
            notification.save_to_db()
            
            return {
                "message": "Service request marked as completed", 
                "service_request": service_request.to_dict()
            }, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
    def _handle_close(self, service_request, customer):
        if service_request.status != 'completed':
            return {"message": "Only completed service requests can be closed"}, 400
        
        if service_request.customer_id != customer.id:
            return {"message": "Not authorized to close this service request"}, 403
        
        service_request.status = 'closed'

        try:
            service_request.save_to_db()
            notification = Notification(
                user_id=service_request.professional.user_id,
                type='request_closed',
                message=f"Service request # {service_request.id} has been closed by the customer."
            )
            notification.save_to_db()
            return {
                "message": "Service request closed successfully", 
                "service_request": service_request.to_dict()
            }, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500


class RejectedServiceRequestResource(Resource):
    """Resource for rejected service request operations"""
    
    @jwt_required()
    def get(self, request_id=None):
        """Get rejected service requests based on user role"""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        
        
        if user.role not in ['admin', 'professional']:
            return {"message": "Unauthorized access"}, 403
        
        
        def add_rejection_flag(rejections, professional_id):
            result = []
            for rejection in rejections:
                rejection_dict = rejection.to_dict()
                rejection_dict['is_own_rejection'] = (rejection.professional_id == professional_id)
                result.append(rejection_dict)
            return result
        
        
        def enrich_rejection_data(rejections):
            result = []
            for rejection in rejections:
                rejection_dict = rejection.to_dict()
                
        
                service_request = ServiceRequest.query.get(rejection.service_request_id)
                if service_request:
        
                    service = Service.query.get(service_request.service_id)
                    if service:
                        rejection_dict['service_name'] = service.name
                    
        
                    customer = Customer.query.get(service_request.customer_id)
                    if customer and customer.user:
                        rejection_dict['customer_name'] = customer.user.name
                
                result.append(rejection_dict)
            return result
        
        
        if request_id:
        
            service_request = ServiceRequest.query.get_or_404(request_id)
            
            if user.role == 'professional':
                professional = Professional.query.filter_by(user_id=user.id).first_or_404()
                
        
                if service_request.service_id != professional.service_id:
                    return {"message": "This service request does not match your service type"}, 403
                
        
                rejections = RejectedServiceRequest.query.filter_by(
                    service_request_id=request_id
                ).all()
                
        
                result = add_rejection_flag(rejections, professional.id)
                
                return {
                    "rejections": result,
                    "count": len(result)
                }, 200
            
        
            elif user.role == 'admin':
                rejections = RejectedServiceRequest.query.filter_by(
                    service_request_id=request_id
                ).all()
                
                result = enrich_rejection_data(rejections)
                
                return {
                    "rejections": result,
                    "count": len(result)
                }, 200
        
        
        if user.role == 'professional':
            professional = Professional.query.filter_by(user_id=user.id).first_or_404()
            
            
            rejections = RejectedServiceRequest.query.filter_by(
                professional_id=professional.id
            ).all()
            
            
            result = enrich_rejection_data(rejections)
                
            return {
                "rejections": result,
                "count": len(result)
            }, 200
                
        elif user.role == 'admin':
            
            query = RejectedServiceRequest.query
            
            
            service_request_id = request.args.get('service_request_id', type=int)
            professional_id = request.args.get('professional_id', type=int)
            
            if service_request_id:
                query = query.filter_by(service_request_id=service_request_id)
            if professional_id:
                query = query.filter_by(professional_id=professional_id)
                
            rejections = query.all()
            
            
            result = enrich_rejection_data(rejections)
            
            return {
                "rejections": result,
                "count": len(result)
            }, 200