from celery import Celery
from flask import Flask
import os
from celery.schedules import crontab

def create_celery_app(app=None):
    app = app or Flask(__name__)

    celery = Celery(
        app.import_name,
        broker = 'redis://localhost:6379/0',
        backend = 'redis://localhost:6379/0',
        include=['tasks.reminder_tasks', 'tasks.report_tasks', 'tasks.export_tasks', 'tasks.service_tasks' ]
    )

    celery.conf.update(
        result_expires=3600,
        timezone='UTC',
        broken_connection_retry=True,
        broken_connection_retry_on_startup=True,
        broker_connection_max_retries=10,
        broker_pool_limit=None,
        broker_heartbeat=10,
        broker_connection_timeout=30,
        beat_schedule= {
            'send_daily_reminders': {
                'task':'tasks.reminder_tasks.send_daily_reminders',
                'schedule': crontab(hour=18,minute=0),
            },
            'check_overdue_requests': {
                'task': 'tasks.reminder_tasks.check_overdue_requests',
                'schedule': crontab(hour=9, minute=0),
            },
            'monthly-reports':{
                'task':'tasks.report_tasks.send_monthly_activity_report',
                'schedule': crontab(day_of_month=1, hour=0, minute=0),
            },
            'auto_cancel_expired_requests': {
                'task': 'tasks.service_tasks.auto_cancel_expired_requests',
                'schedule': crontab(minute='*/10'),
            }
        }
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
            
    celery.Task = ContextTask
    return celery