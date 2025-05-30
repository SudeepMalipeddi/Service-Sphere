from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models import User

def role_required(roles):
    """Decorator to require at least one role from a list."""
    
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return {"message": "User not found"}, 404
            
            if not user.is_active:
                return {"message": "User account is inactive"}, 403
            
            if user.role not in roles and user.role != 'admin':
                return {"message": "Access denied. Required roles: " + ", ".join(roles)}, 403
            
            return fn(*args, **kwargs)
        
        return wrapper
    return decorator


admin_required = role_required(['admin'])
customer_required = role_required(['customer'])
professional_required = role_required(['professional'])