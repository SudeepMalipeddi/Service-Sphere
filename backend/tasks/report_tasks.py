from celery import shared_task
from models.models import Customer, ServiceRequest, User
from datetime import datetime, timedelta
import os
import jinja2
from flask import current_app
from mail_config import mail
from flask_mail import Message

@shared_task
def send_monthly_activity_report():
    today = datetime.utcnow()
    first_day_of_month = datetime(today.year, today.month, 1)
    last_month = first_day_of_month - timedelta(days=1)
    month_num = last_month.month
    year_num = last_month.year
    customers = Customer.query.join(User).filter(User.is_active == True).all()
    reports_generated = 0
    
    for customer in customers:
        try:
            
            start_date = datetime(year_num, month_num, 1)
            if month_num == 12:
                end_date = datetime(year_num + 1, 1, 1)
            else:
                end_date = datetime(year_num, month_num + 1, 1)
            
            request_count = ServiceRequest.query.filter(
                ServiceRequest.customer_id == customer.id,
                ServiceRequest.request_date >= start_date,
                ServiceRequest.request_date < end_date
            ).count()
            report_path = generate_customer_report(customer, month_num, year_num)

            if report_path:
                send_report_email(customer,report_path,month_num,year_num)
                reports_generated += 1
        except Exception as e:
            current_app.logger.error(f"Failed to generate report for customer {customer.id}: {str(e)}")
    
    return f"Generated monthly reports for {reports_generated} customers"

def generate_customer_report(customer, month, year):
    
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    requests = ServiceRequest.query.filter(
        ServiceRequest.customer_id == customer.id,
        ServiceRequest.request_date >= start_date,
        ServiceRequest.request_date < end_date
    ).all()

    if not requests:
        return None
    
    report_data = {
        'customer_name': customer.user.name,
        'month': start_date.strftime('%B %Y'),
        'total_requests': len(requests),
        'completed_requests': sum(1 for r in requests if r.status == 'closed'),
        'pending_requests': sum(1 for r in requests if r.status in ['requested', 'assigned']),
        'cancelled_requests': sum(1 for r in requests if r.status == 'cancelled'),
        'total_spent': sum(r.service.base_price for r in requests if r.status == 'closed'),
        'requests': [
            {
                'id': r.id,
                'service_name': r.service.name,
                'status': r.status,
                'request_date': r.request_date.strftime('%Y-%m-%d'),
                'completion_date': r.completion_date.strftime('%Y-%m-%d') if r.completion_date else None,
                'professional_name': r.professional.user.name if r.professional else None,
                'price': r.service.base_price,
                'rating': r.reviews[0].rating if r.reviews else None
            }
            for r in requests
        ]
    }

    templates_dir = os.path.join(current_app.root_path, 'templates')
    os.makedirs(templates_dir, exist_ok=True)

    template_path = os.path.join(templates_dir, 'monthly_report.html')
    if not os.path.exists(template_path):
        create_report_template(template_path)

    with open(template_path, 'r') as f:
        template_content = f.read()
        
    template = jinja2.Template(template_content)
    html_output = template.render(**report_data)

    reports_dir = os.path.join(current_app.root_path, 'static', 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    file_path = os.path.join(
        reports_dir, 
        f"customer_{customer.id}_report_{year}_{month}.html"
    )
    
    with open(file_path, 'w') as f:
        f.write(html_output)
    
    return file_path


def create_report_template(template_path):
    """Create the monthly report HTML template"""
    template_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Monthly Activity Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2 {
            color: #2c3e50;
        }
        .header {
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .summary {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        .summary-item {
            margin-bottom: 10px;
        }
        .summary-item .label {
            font-weight: bold;
            color: #7f8c8d;
        }
        .summary-item .value {
            font-size: 1.2em;
            color: #2c3e50;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #3498db;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .status {
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.85em;
        }
        .status-closed {
            background-color: #2ecc71;
            color: white;
        }
        .status-requested {
            background-color: #f39c12;
            color: white;
        }
        .status-assigned {
            background-color: #3498db;
            color: white;
        }
        .status-cancelled {
            background-color: #e74c3c;
            color: white;
        }
        .footer {
            margin-top: 40px;
            text-align: center;
            font-size: 0.9em;
            color: #7f8c8d;
            border-top: 1px solid #eee;
            padding-top: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Monthly Activity Report</h1>
        <p>Customer: {{ customer_name }}</p>
        <p>Period: {{ month }}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <div class="summary-grid">
            <div class="summary-item">
                <div class="label">Total Requests:</div>
                <div class="value">{{ total_requests }}</div>
            </div>
            <div class="summary-item">
                <div class="label">Completed Requests:</div>
                <div class="value">{{ completed_requests }}</div>
            </div>
            <div class="summary-item">
                <div class="label">Pending Requests:</div>
                <div class="value">{{ pending_requests }}</div>
            </div>
            <div class="summary-item">
                <div class="label">Cancelled Requests:</div>
                <div class="value">{{ cancelled_requests }}</div>
            </div>
            <div class="summary-item">
                <div class="label">Total Spent:</div>
                <div class="value">₹{{ total_spent }}</div>
            </div>
        </div>
    </div>
    
    <h2>Service Requests</h2>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Service</th>
                <th>Status</th>
                <th>Date</th>
                <th>Professional</th>
                <th>Price</th>
                <th>Rating</th>
            </tr>
        </thead>
        <tbody>
            {% for request in requests %}
            <tr>
                <td>{{ request.id }}</td>
                <td>{{ request.service_name }}</td>
                <td>
                    <span class="status status-{{ request.status }}">{{ request.status }}</span>
                </td>
                <td>{{ request.request_date }}</td>
                <td>{{ request.professional_name or '-' }}</td>
                <td>₹{{ request.price }}</td>
                <td>{{ request.rating or '-' }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <div class="footer">
        <p>Thank you for using Service Sphere!</p>
    </div>
</body>
</html>
"""
    with open(template_path, 'w') as f:
        f.write(template_content)
    
    return True

def send_report_email(customer, report_path, month, year):
    """
    Send email with attached monthly report using Flask-Mail
    """
    if not customer.user.email:
        return False
    
    month_name = datetime(year, month, 1).strftime('%B %Y')
    
    try:
        
        msg = Message(
            subject=f"Your Monthly Activity Report - {month_name}",
            recipients=[customer.user.email]
        )
        
        
        msg.body = f"""Dear {customer.user.name},

Please find attached your monthly activity report for {month_name}.
Thank you for using our platform.

Regards,
The Service Sphere Team
"""
        with open(report_path, 'r') as f:
            msg.html = f.read()

        current_app.logger.info(f"Sending report email to {customer.user.email}")
        mail.send(msg)
        
        current_app.logger.info(f"Report email sent to {customer.user.email}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send report email: {str(e)}")
        return False