from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from datetime import timedelta
import os
from dotenv import load_dotenv

from models import db,User

from resources.admin import AdminDashboardResource,AdminCustomersResource,AdminProfessionalsResource
from resources.auth import UserRegister, UserLogin, UserRefresh, UserLogout
from resources.customer import CustomerResource, CustomerListResource
from resources.export import ExportResource
from resources.professional import ProfessionalResource, ProfessionalListResource, ProfessionalVerificationResource
from resources.service import ServiceResource, ServiceListResource
from resources.service_request import ServiceRequestResource,ServiceRequestActionResource,ServiceRequestListResource,RejectedServiceRequest,RejectedServiceRequestResource
from resources.notification import NotificationResource, NotificationListResource
from resources.review import ReviewListResource,ReviewResource

from mail_config import init_mail

# celery
from celery_config import create_celery_app


def create_app(test_config=None):
    app = Flask(__name__,static_folder='static')

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-not-secure'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URI', 'sqlite:///household_services.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key'),
            JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=1),
            JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=30),
            JWT_BLACKLIST_ENABLED=True,
            JWT_BLACKLIST_TOKEN_CHECKS=['access', 'refresh'],
            UPLOAD_FOLDER=os.path.join(app.root_path, 'static', 'uploads'),
            MAX_CONTENT_LENGTH=16 * 1024 * 1024,
            REDIS_URL=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),


            MAIL_SERVER=('localhost'),
            MAIL_PORT=1025,
            MAIL_USE_TLS=False,
            MAIL_USE_SSL=False,
            MAIL_USERNAME=os.environ.get('MAIL_USERNAME',None),
            MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD',None),
            MAIL_DEFAULT_SENDER=os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@household-services.com'),
        )
    else:
        app.config.from_mapping(test_config)

    CORS(app)
    db.init_app(app)
    jwt = JWTManager(app)
    api = Api(app)
    celery = create_celery_app(app)
    app.celery = celery
    init_mail(app)
    
    
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'static', 'exports'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'static', 'reports'), exist_ok=True)
    
    # Authentication endpoints
    api.add_resource(UserRegister,'/api/register')
    api.add_resource(UserLogin, '/api/login')
    api.add_resource(UserRefresh, '/api/refresh')
    api.add_resource(UserLogout, '/api/logout')


    # Admin endpoints
    api.add_resource(AdminDashboardResource, '/api/admin/dashboard')
    api.add_resource(AdminProfessionalsResource, '/api/admin/professionals')
    api.add_resource(AdminCustomersResource, '/api/admin/customers')
    api.add_resource(ExportResource, '/api/admin/export')

    # Customer endpoints
    api.add_resource(CustomerResource, '/api/customers/<int:customer_id>')
    api.add_resource(CustomerListResource, '/api/customers')

    # Professional endpoints
    api.add_resource(ProfessionalListResource, '/api/professionals')
    api.add_resource(ProfessionalResource, '/api/professionals/<int:professional_id>')
    api.add_resource(ProfessionalVerificationResource, '/api/professionals/<int:professional_id>/verify')
    
    # Review
    api.add_resource(ReviewListResource, '/api/reviews')
    api.add_resource(ReviewResource, '/api/reviews/<int:review_id>')


    # Service endpoints
    api.add_resource(ServiceListResource, '/api/services')
    api.add_resource(ServiceResource, '/api/services/<int:service_id>')

    # Service Request endpoints
    api.add_resource(ServiceRequestListResource, '/api/service-requests')
    api.add_resource(ServiceRequestResource, '/api/service-requests/<int:request_id>')
    api.add_resource(ServiceRequestActionResource, '/api/service-requests/<int:request_id>/action')

    # Rejected Service Request endpoints
    api.add_resource(RejectedServiceRequestResource, '/api/rejected-requests', '/api/rejected-requests/<int:request_id>')

    # Notification endpoints
    api.add_resource(NotificationListResource, '/api/notifications')
    api.add_resource(NotificationResource, '/api/notifications/<int:notification_id>')



    with app.app_context():
        db.create_all()
        migrate = Migrate(app,db)
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                email='admin@example.com',
                name='Administrator',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Admin user created')

    return app,migrate,celery

app, migrate, celery = create_app()


if __name__ == '__main__':
    app.run(debug=True)