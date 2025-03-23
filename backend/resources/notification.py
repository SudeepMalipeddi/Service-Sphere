from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Notification
from flask import request

class NotificationResource(Resource):

    @jwt_required()
    def get(self, notification_id):

        current_user_id = get_jwt_identity()
        notification = Notification.query.filter_by(id=notification_id)

        if notification.user_id != current_user_id:
            return {"message": "Not authorized to view this notification"}, 403
        
        return {"notification": notification.to_dict()}, 200
    
    @jwt_required()
    def put(self, notification_id):

        current_user_id = get_jwt_identity()

        notification = Notification.query.filter(Notification.id == notification_id).first()

        if int(notification.user_id) != int(current_user_id):
            return {"message": "Not authorized to update this notification"}, 403
        
        notification.is_read = True

        try:
            notification.save_to_db()
            return {"message": "Notification marked as read", "notification": notification.to_dict()}, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
    @jwt_required()
    def delete(self, notification_id):

        current_user_id = get_jwt_identity()

        notification = Notification.query.filter(Notification.id == notification_id).first()

        if int(notification.user_id) != int(current_user_id):
            return {"message": "Not authorized to delete this notification"}, 403
            
        try:
            notification.delete_from_db()
            return {"message": "Notification deleted successfully"}, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        

class NotificationListResource(Resource):

    @jwt_required()
    def get(self):
        """Get user's notifications"""
        current_user_id = get_jwt_identity()

        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        limit = request.args.get('limit', type=int)

        query = Notification.query.filter_by(user_id=current_user_id)

        if unread_only:
            query = query.filter_by(is_read=False)

        notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()

        unread_count = Notification.query.filter_by(user_id=current_user_id, is_read=False).count()

        return {
            "notifications": [notification.to_dict() for notification in notifications],
            "unread_count": unread_count
        }, 200
    
    @jwt_required()
    def put(self):
        current_user_id = get_jwt_identity()
        
        unread_notifications = Notification.query.filter_by(user_id=current_user_id, is_read=False).all()
        
        for notification in unread_notifications:
            notification.is_read = True
            
        try:
            for notification in unread_notifications:
                notification.save_to_db()
                
            return {"message": f"Marked {len(unread_notifications)} notifications as read"}, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500