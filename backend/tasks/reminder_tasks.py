from celery import shared_task
from models.models import ServiceRequest, Professional, Notification
from flask import current_app
from mail_config import mail
from flask_mail import Message
from datetime import datetime

@shared_task
def send_daily_reminders():
    """
    Send daily reminders to professionals for pending service requests.
    This task runs every evening at 6 PM.
    """
    
    pending_requests = ServiceRequest.query.filter(
        ServiceRequest.status.in_(['requested', 'assigned']),
        ServiceRequest.professional_id.isnot(None)
    ).all()
    
    professionals_notified = set()
    
    for request in pending_requests:
        if request.professional_id and request.professional_id not in professionals_notified:
            professional = Professional.query.get(request.professional_id)
            
            if not professional:
                continue
                
            pending_count = ServiceRequest.query.filter(
                ServiceRequest.professional_id == professional.id,
                ServiceRequest.status.in_(['requested', 'assigned'])
            ).count()
            
            
            notification = Notification(
                user_id=professional.user_id,
                type='reminder',
                message=f"You have {pending_count} pending service request(s). Please take action."
            )
            notification.save_to_db()
            
            
            send_external_notification(professional.user, notification.message)
            
            professionals_notified.add(professional.id)
    
    return f"Sent reminders to {len(professionals_notified)} professionals"


def send_external_notification(user, message):
    """
    Helper function to send notifications through external services
    """
    if(user.email):
        try:
            msg = Message(
                subject="Service Sphere Notification",
                recipients=[user.email],
                body=f"Hello {user.name},\n\n{message}\n\nBest regards, \n Service Sphere Team"
            )
            mail.send(msg)
            current_app.logger.info(f"Email sent to {user.email}")
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {str(e)}")
    
    
    
    current_app.logger.info(f"Notification for {user.name} ({user.email}): {message}")
    return False


@shared_task
def check_overdue_requests():
    """
    Check for service requests that are overdue
    """
    # Find requests that are scheduled for completion but still open
    today = datetime.utcnow()
    overdue_requests = ServiceRequest.query.filter(
        ServiceRequest.status.in_(['assigned']),
        ServiceRequest.scheduled_date < today
    ).all()
    
    for request in overdue_requests:
        # Notify customer
        customer_notification = Notification(
            user_id=request.customer.user_id,
            type='overdue',
            message=f"Your service request #{request.id} is overdue. We'll follow up with the professional."
        )
        customer_notification.save_to_db()
        
        # Notify professional
        if request.professional:
            prof_notification = Notification(
                user_id=request.professional.user_id,
                type='overdue',
                message=f"Service request #{request.id} is overdue. Please update the status or contact the customer."
            )
            prof_notification.save_to_db()
            
            # Send notification through external service
            send_external_notification(request.professional.user, prof_notification.message)
    
    return f"Processed {len(overdue_requests)} overdue requests"
