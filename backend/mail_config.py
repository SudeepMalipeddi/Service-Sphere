from flask_mail import Mail, Message

# Initialize Flask-Mail
mail = Mail()

def init_mail(app):
    """Initialize Flask-Mail with the Flask app"""
    app.config.update(
        MAIL_SERVER=app.config.get('MAIL_SERVER', 'localhost'),
        MAIL_PORT=app.config.get('MAIL_PORT', 1025),
        MAIL_USE_TLS=app.config.get('MAIL_USE_TLS', False),
        MAIL_USERNAME=app.config.get('MAIL_USERNAME', None),
        MAIL_PASSWORD=app.config.get('MAIL_PASSWORD', None),
        MAIL_DEFAULT_SENDER=app.config.get('MAIL_DEFAULT_SENDER', 'noreply@servicesphere.com')
    )
    mail.init_app(app)
    return mail