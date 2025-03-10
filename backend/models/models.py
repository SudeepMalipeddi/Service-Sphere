from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'customer', 'professional'
    phone = db.Column(db.String(20))
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    customer = db.relationship('Customer', backref='user', uselist=False, cascade="all, delete-orphan")
    professional = db.relationship('Professional', backref='user', uselist=False, cascade="all, delete-orphan")
    notifications = db.relationship('Notification', backref='user', cascade="all, delete-orphan")
    export_tasks = db.relationship('ExportTask', backref='user', cascade="all, delete-orphan")
    monthly_reports = db.relationship('MonthlyReport', backref='user', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }


class Customer(db.Model):
    
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    address = db.Column(db.String(255))
    pincode = db.Column(db.String(10))
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    service_requests = db.relationship('ServiceRequest', backref='customer', cascade="all, delete-orphan")
    reviews = db.relationship('Review', backref='customer', cascade="all, delete-orphan")
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.user.name,
            'email': self.user.email,
            'phone': self.user.phone,
            'address': self.address,
            'pincode': self.pincode,
            'registered_on': self.registered_on.isoformat() if self.registered_on else None
        }


class Service(db.Model):
    
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    base_price = db.Column(db.Float, nullable=False)
    estimated_time = db.Column(db.Integer)  # in minutes
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    professionals = db.relationship('Professional', backref='service')
    service_requests = db.relationship('ServiceRequest', backref='service')
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'base_price': self.base_price,
            'estimated_time': self.estimated_time,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Professional(db.Model):
    
    __tablename__ = 'professionals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    bio = db.Column(db.Text)
    years_experience = db.Column(db.Integer, default=0)
    verification_status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    documents_url = db.Column(db.Text)  
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    service_requests = db.relationship('ServiceRequest', backref='professional')
    rejected_requests = db.relationship('RejectedServiceRequest', backref='professional', cascade="all, delete-orphan")
    reviews = db.relationship('Review', backref='professional')
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        
    def get_average_rating(self):
        if not self.reviews:
            return 0
        total = sum(review.rating for review in self.reviews)
        return round(total / len(self.reviews), 1)
    
    def to_dict(self):
        avg_rating = self.get_average_rating()
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.user.name,
            'email': self.user.email,
            'phone': self.user.phone,
            'service_id': self.service_id,
            'service_name': self.service.name if self.service else None,
            'bio': self.bio,
            'years_experience': self.years_experience,
            'verification_status': self.verification_status,
            'documents_url': self.documents_url,
            'registered_on': self.registered_on.isoformat() if self.registered_on else None,
            'rating': avg_rating
        }


class ServiceRequest(db.Model):
    
    __tablename__ = 'service_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=True)
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    completion_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='requested')  # 'requested', 'assigned', 'in_progress', 'completed', 'closed', 'cancelled'
    remarks = db.Column(db.Text)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
    reviews = db.relationship('Review', backref='service_request', cascade="all, delete-orphan")
    rejected_by = db.relationship('RejectedServiceRequest', backref='service_request', cascade="all, delete-orphan")
    
    __table_args__ = (
        db.CheckConstraint("status IN ('requested', 'assigned', 'in_progress', 'completed', 'closed', 'cancelled')"),
        db.Index('idx_service_request_status', 'status'),
        db.Index('idx_service_request_dates', 'request_date', 'completion_date'),
    )
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.user.name,
            'service_id': self.service_id,
            'service_name': self.service.name,
            'professional_id': self.professional_id,
            'professional_name': self.professional.user.name if self.professional else None,
            'request_date': self.request_date.isoformat() if self.request_date else None,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'status': self.status,
            'remarks': self.remarks,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


class RejectedServiceRequest(db.Model):
    
    __tablename__ = 'rejected_service_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id', ondelete='CASCADE'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    reason = db.Column(db.Text)
    rejected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        return {
            'id': self.id,
            'service_request_id': self.service_request_id,
            'professional_id': self.professional_id,
            'professional_name': self.professional.user.name,
            'reason': self.reason,
            'rejected_at': self.rejected_at.isoformat() if self.rejected_at else None
        }


class Review(db.Model):
    
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id', ondelete='CASCADE'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        return {
            'id': self.id,
            'service_request_id': self.service_request_id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.user.name,
            'professional_id': self.professional_id,
            'professional_name': self.professional.user.name,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Notification(db.Model):
    
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'request', 'approval', 'reminder', etc.
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ExportTask(db.Model):
    
    __tablename__ = 'export_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    export_type = db.Column(db.String(50), nullable=False)  # 'service_requests', 'professionals', etc.
    status = db.Column(db.String(20), default='pending')  # 'pending', 'processing', 'completed', 'failed'
    file_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'export_type': self.export_type,
            'status': self.status,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class MonthlyReport(db.Model):
    
    __tablename__ = 'monthly_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    report_type = db.Column(db.String(50), nullable=False) 
    file_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'month': self.month,
            'year': self.year,
            'report_type': self.report_type,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }