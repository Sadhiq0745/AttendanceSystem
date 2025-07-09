import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_alert_email(receiver_email, student_name, attendance_percent):
    sender_email = "attendance.alerts.college@gmail.com"  # Your Gmail
    app_password = "dscfbtovwcalfjwt"  # Paste the app password here

    subject = "⚠️ Low Attendance Alert"
    body = f"""
    

    Dear {student['name']},

        This is to inform you that your current attendance percentage is {student['percentage']}%.
        Please ensure that you maintain minimum required attendance in upcoming sessions.
        Regards,
        Admin Team
            
    """

    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # SMTP Server Connection
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)

        print(f"✅ Alert email sent to {receiver_email}")

    except Exception as e:
        print(f"❌ Failed to send email to {receiver_email}: {e}")


if __name__ == "__main__":
    # Example student data
    students_below_75 = [
        {"name": "dharni", "email": "rasikaraju069@gmail.com", "attendance_percent": 60},
        {"name": "John Doe", "email": "john.doe@example.com", "attendance_percent": 72},
    ]

    for student in students_below_75:
        send_alert_email(student['email'], student['name'], student['attendance_percent'])
