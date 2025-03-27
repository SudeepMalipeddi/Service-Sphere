from celery import shared_task
from models import ServiceRequest, ExportTask, User, Notification
from datetime import datetime
import os
import csv
from flask import current_app
from mail_config import mail
from flask_mail import Message

@shared_task
def export_service_requests_to_csv(export_id):
    """
    Export service requests to CSV and email to admin
    """
    export_task = ExportTask.query.get(export_id)
    if not export_task:
        current_app.logger.error(f"Export task {export_id} not found")
        return "Export task not found"
    
    try:
        export_task.status = 'processing'
        export_task.save_to_db()
        
        exports_dir = os.path.join(current_app.root_path, 'static', 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        filename = f"service_requests_{timestamp}.csv"
        filepath = os.path.join(exports_dir, filename)
        
        success = export_service_requests(filepath)
        
        if success:
            export_task.status = 'completed'
            export_task.file_path = f"static/exports/{filename}"
            export_task.completed_at = datetime.utcnow()
            export_task.save_to_db()
            
            notification = Notification(
                user_id=export_task.user_id,
                type='export_complete',
                message="Your service requests export is ready. A copy has been sent to your email."
            )
            notification.save_to_db()
            
            admin = User.query.get(export_task.user_id)
            if admin and admin.email:
                send_csv_to_admin(admin.email, filepath)
            
            return f"Export task {export_id} completed successfully"
        else:
            export_task.status = 'failed'
            export_task.save_to_db()
            
            notification = Notification(
                user_id=export_task.user_id,
                type='export_failed',
                message="Your service requests export could not be generated."
            )
            notification.save_to_db()
            
            return f"Export failed"
            
    except Exception as e:
        export_task.status = 'failed'
        export_task.save_to_db()
        
        notification = Notification(
            user_id=export_task.user_id,
            type='export_failed',
            message=f"Your service requests export failed: {str(e)}"
        )
        notification.save_to_db()

        print(f"Error exporting service requests: {str(e)}")
        current_app.logger.error(f"Error exporting service requests: {str(e)}")
        
        return f"Export failed with error: {str(e)}"

def export_service_requests(filepath):
    """
    Export all service requests to CSV
    """
    try:
        
        requests = ServiceRequest.query.all()
        
        
        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = [
                'ID', 'Customer', 'Service', 'Professional',
                'Request Date', 'Scheduled Date', 'Completion Date', 
                'Status', 'Price', 'Remarks'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for req in requests:
                writer.writerow({
                    'ID': req.id,
                    'Customer': req.customer.user.name,
                    'Service': req.service.name,
                    'Professional': req.professional.user.name if req.professional else "Not Assigned",
                    'Request Date': req.request_date.strftime('%Y-%m-%d') if req.request_date else "N/A",
                    'Scheduled Date': req.scheduled_date.strftime('%Y-%m-%d') if req.scheduled_date else "N/A",
                    'Completion Date': req.completion_date.strftime('%Y-%m-%d') if req.completion_date else "N/A",
                    'Status': req.status,
                    'Price': req.service.base_price,
                    'Remarks': req.remarks or "None"
                })
        
        return True
        
    except Exception as e:
        current_app.logger.error(f"Error exporting service requests: {str(e)}")
        return False

def send_csv_to_admin(email, filepath):
    """
    Send the CSV export to the admin's email
    """
    try:
        msg = Message(
            subject="Service Sphere - Service Requests Export",
            recipients=[email],
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'no_reply@example.com')
        )
        
        msg.body = f"""Hello,

Your service requests export has been completed.
The file is attached to this email.

Thank you for using Service Sphere.

Best regards,
Service Sphere Team
"""
        
        with open(filepath, 'rb') as fp:
            msg.attach(
                filename=os.path.basename(filepath),
                content_type='text/csv',
                data=fp.read()
            )
        
        mail.send(msg)
        current_app.logger.info(f"Export email sent to {email}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send export email: {str(e)}")
        return False
    