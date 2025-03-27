from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Customer,User,ServiceRequest,ExportTask
from utils import admin_required
from flask import request
from tasks.export_tasks import export_service_requests_to_csv

class ExportResource(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        current_user_id = get_jwt_identity()

        export_task = ExportTask(
            user_id=current_user_id,
            export_type='service_requests',
            status='pending'
        )
        export_task.save_to_db()

        try:
            from app import celery
            
            if 'tasks.export_tasks.export_service_requests_to_csv' not in celery.tasks:
                return {"message": "Task not registered with Celery"}, 500
                
            print("Task is registered with Celery")
            
            task = celery.send_task(
                'tasks.export_tasks.export_service_requests_to_csv',
                args=[export_task.id],
            )
            print(f"Task sent to Celery: {task.id}")
            
            return {
                "message": "Export task created successfully",
                "task_id": export_task.id
            }, 202
        except ImportError as e:
            print(f"Import error: {str(e)}")
            return {"message": f"Import error: {str(e)}"}, 500
        except ConnectionRefusedError as e:
            print(f"Connection refused: {str(e)}")
            return {"message": f"Connection refused: {str(e)}"}, 500
        except Exception as e:
            print(f"Error while creating export task: {e}")
            return {
                "message": "Error while creating export task",
                "error": str(e)
            }, 500