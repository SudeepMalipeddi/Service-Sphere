from celery import shared_task
from models import ServiceRequest, Notification
from datetime import datetime 
from flask import current_app

@shared_task
def auto_cancel_expired_requests():

    now = datetime.utcnow()

    expired_requests = ServiceRequest.query.filter(
        ServiceRequest.status == 'requested',
        ServiceRequest.professional_id.is_(None),
        ServiceRequest.scheduled_date < now
    ).all()

    cancelled_count = 0

    for request in expired_requests:
        try:
            request.status = 'cancelled'
            request.save_to_db()

            notification = Notification(
                user_id=request.customer.user_id,
                type='request_auto_cancelled',
                message=f"Your service request #{request.id} has been automatically cancelled because no professional accepted it before the scheduled date."
            )

            notification.save_to_db()

            cancelled_count += 1

            current_app.logger.info(f"Auto-cancelled service request #{request.id} for customer #{request.customer_id}")

        except Exception as e:
            current_app.logger.error(f"Error auto-cancelling request #{request.id}: {str(e)}")
            
    return f"Auto-cancelled {cancelled_count} expired service requests"
