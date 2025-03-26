from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Review, Service, ServiceRequest,Customer, Professional,User,Notification
from utils import customer_required
from flask import request


class ReviewResource(Resource):

    @jwt_required()
    def get(self, review_id):
        """Get a specific review by ID"""
        review = Review.query.get_or_404(review_id)
        return {"review": review.to_dict()}, 200
    
    @jwt_required()
    @customer_required
    def put(self, review_id):

        current_user_id = get_jwt_identity()
        customer = Customer.query.filter_by(user_id = current_user_id).first_or_404()

        review = Review.query.get_or_404(review_id)

        if review.customer_id != customer.id:
            return {"message": "You are not authorized to update this review."}, 403
        
        parser = reqparse.RequestParser()
        parser.add_argument("rating", type=int)
        parser.add_argument("comment", type=str)

        data = parser.parse_args()

        if data['rating'] is not None:
            if not 1 <= data['rating'] <= 5:
                return {"message": "Rating must be between 1 and 5"}, 400
            review.rating = data['rating']
            
        if data['comment'] is not None:
            review.comment = data['comment']

        try:
            review.save_to_db()

            notification = Notification(
                user_id=review.professional.user_id,
                type='review_updated',
                message=f"A customer has updated their review for your service."
            )
            notification.save_to_db()

            return {"message": "Review updated successfully", "review": review.to_dict()}, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
    @jwt_required()
    @customer_required
    def delete(self, review_id):
        """Delete a review (customer only)"""
        current_user_id = get_jwt_identity()
        customer = Customer.query.filter_by(user_id=current_user_id).first_or_404()
        
        review = Review.query.get_or_404(review_id)
        
        # Ensure the customer owns this review
        if review.customer_id != customer.id:
            return {"message": "Not authorized to delete this review"}, 403
            
        try:
            review.delete_from_db()
            return {"message": "Review deleted successfully"}, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500


class ReviewListResource(Resource):

    def get(self):

        professional_id = request.args.get('professional_id', type=int)
        service_id = request.args.get('service_id', type=int)
        service_request_id = request.args.get('service_request_id', type=int)
        customer_id = request.args.get('customer_id', type=int)

        query = Review.query

        if professional_id:
            query = query.filter_by(professional_id=professional_id)
            
        if service_id:
            query = query.filter_by(service_id=service_id)
            
        if service_request_id:
            query = query.filter_by(service_request_id=service_request_id)
            
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
            
        reviews = query.all()
        
        return {"reviews": [review.to_dict() for review in reviews]}, 200

    @jwt_required()
    @customer_required
    def post(self):
        
        current_user_id = get_jwt_identity()
        customer = Customer.query.filter_by(user_id=current_user_id).first_or_404()
        
        parser = reqparse.RequestParser()
        parser.add_argument('service_request_id', type=int, required=True, help="Service request ID is required")
        parser.add_argument('rating', type=int, required=True, help="Rating is required")
        parser.add_argument('comment', type=str)
        
        data = parser.parse_args()
        
        
        if not 1 <= data['rating'] <= 5:
            return {"message": "Rating must be between 1 and 5"}, 400
            
        
        service_request = ServiceRequest.query.get(data['service_request_id'])
        if not service_request:
            return {"message": "Service request not found"}, 404
            
        
        if service_request.customer_id != customer.id:
            return {"message": "Not authorized to review this service request"}, 403
            
        if service_request.status != 'closed':
            return {"message": "Can only review closed service requests"}, 400
            
        existing_review = Review.query.filter_by(service_request_id=service_request.id).first()
        if existing_review:
            return {"message": "You have already reviewed this service request"}, 400
            
        new_review = Review(
            service_request_id=service_request.id,
            customer_id=customer.id,
            professional_id=service_request.professional_id,
            rating=data['rating'],
            comment=data.get('comment', '')
        )
        
        try:
            new_review.save_to_db()
            
            notification = Notification(
                user_id=service_request.professional.user_id,
                type='new_review',
                message=f"A customer has left a review for your service."
            )
            notification.save_to_db()
            
            return {"message": "Review created successfully", "review": new_review.to_dict()}, 201
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500