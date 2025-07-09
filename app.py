"""
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import os
from firebase_config import db, bucket

from firebase_admin import db
from firebase_admin import storage


# Initialize Firebas
#initialize_firebase()

# Flask app initialization
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session

# --------------------- Admin Web Login ------------------------

# @app.route('/')
# def home():
#     if 'admin' in session:
#         return "✅ Welcome Admin! You are logged in. <a href='/logout'>Logout</a>"
#     return render_template('login.html')
@app.route('/')
def home():
    if 'admin' in session:
        return render_template('dashboard.html')
    return render_template('login.html')



@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Fetch admin data from Firebase
    admin_ref = db.reference('admins/admin1')
    admin_data = admin_ref.get()

    if admin_data and admin_data['username'] == username and admin_data['password'] == password:
        session['admin'] = username
        return redirect(url_for('home'))
    else:
        return "❌ Invalid credentials! <a href='/'>Try again</a>"


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))


# --------------------- Admin Login API ------------------------

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Fetch admin data from Firebase
    admin_ref = db.reference('admins/admin1')
    admin_data = admin_ref.get()

    if admin_data and admin_data['username'] == username and admin_data['password'] == password:
        session['admin'] = username
        return jsonify({"status": "success", "message": "Login successful!"}), 200
    else:
        return jsonify({"status": "failed", "message": "Invalid credentials"}), 401


# --------------------- Protected Route Example ------------------------

@app.route('/api/admin/students', methods=['GET'])
def get_students():
    if 'admin' not in session:
        return jsonify({"status": "failed", "message": "Unauthorized"}), 401

    # Fetch all students data from Firebase
    students_ref = db.reference('students')
    students_data = students_ref.get()

    return jsonify({"status": "success", "students": students_data}), 200


# --------------------- Student Registration ------------------------


@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if 'admin' not in session:
        return redirect(url_for('home'))  # Ensure only logged-in admin can access

    if request.method == 'POST':
        student_id = request.form['student_id']
        student_name = request.form['student_name']
        image_file = request.files['image']

        if not student_id or not student_name or not image_file:
            return "❌ All fields are required! <a href='/register_student'>Try Again</a>"

        # Save student data in Realtime Database
        student_ref = db.reference('students/' + student_id)
        student_ref.set({
            'name': student_name,
            'image': f'student_images/{student_id}.jpg'
        })

        # Upload image to Firebase Storage
        bucket = storage.bucket()
        blob = bucket.blob(f'student_images/{student_id}.jpg')
        blob.upload_from_file(image_file, content_type='image/jpeg')

        return f"✅ Student {student_name} registered successfully! <a href='/register_student'>Add More</a> | <a href='/'>Go to Dashboard</a>"

    return render_template('register_student.html')

@app.route('/students')
def students():
    if 'admin' not in session:
        return redirect(url_for('home'))

    # Fetch students data
    students_ref = db.reference('students')
    students_data = students_ref.get()

    # Process to extract image name
    processed_students = []
    if students_data:
        for student_id, details in students_data.items():
            image_path = details.get('image', '')
            # Extract only the image name without extension and folder
            image_name = os.path.basename(image_path).split('.')[0] if image_path else ''
            processed_students.append({
                'student_id': student_id,
                'name': details.get('name', ''),
                'image_name': image_name
            })

    return render_template('view_students.html', students=processed_students)





# -------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
"""
# after adding the gmail nd the number
import subprocess
import signal
from flask import Flask, render_template, request, redirect, url_for, flash, session
# <== Declare this global variable here
from multiprocessing import Process
import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, session

from firebase_config import db, bucket
from firebase_admin import storage
from flask import send_file
from io import BytesIO
from openpyxl import Workbook
import datetime
camera_process = None


# Flask app initialization
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session

# --------------------- Admin Web Login ------------------------

@app.route('/')
def home():
    if 'admin' in session:
        return render_template('dashboard.html')
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Fetch admin data from Firebase
    admin_ref = db.reference('admins/admin1')
    admin_data = admin_ref.get()

    if admin_data and admin_data['username'] == username and admin_data['password'] == password:
        session['admin'] = username
        return redirect(url_for('home'))
    else:
        return "❌ Invalid credentials! <a href='/'>Try again</a>"


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))


# --------------------- Admin Login API ------------------------

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Fetch admin data from Firebase
    admin_ref = db.reference('admins/admin1')
    admin_data = admin_ref.get()

    if admin_data and admin_data['username'] == username and admin_data['password'] == password:
        session['admin'] = username
        return jsonify({"status": "success", "message": "Login successful!"}), 200
    else:
        return jsonify({"status": "failed", "message": "Invalid credentials"}), 401


# --------------------- Protected Route Example ------------------------

@app.route('/api/admin/students', methods=['GET'])
def get_students():
    if 'admin' not in session:
        return jsonify({"status": "failed", "message": "Unauthorized"}), 401

    # Fetch all students data from Firebase
    students_ref = db.reference('students')
    students_data = students_ref.get()

    return jsonify({"status": "success", "students": students_data}), 200



# --------------------- Student Registration ------------------------

@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if 'admin' not in session:
        return redirect(url_for('home'))  # Ensure only logged-in admin can access

    if request.method == 'POST':
        student_id = request.form['student_id']
        student_name = request.form['student_name']
        mobile_number = request.form['mobile_number']
        email = request.form['email']
        image_file = request.files['image']

        if not student_id or not student_name or not mobile_number or not email or not image_file:
            return "❌ All fields are required! <a href='/register_student'>Try Again</a>"

        # Save student data in Realtime Database
        student_ref = db.reference('students/' + student_id)
        student_ref.set({
            'name': student_name,
            'mobile_number': mobile_number,
            'email': email,
            'image': f'student_images/{student_id}.jpg'
        })

        # Upload image to Firebase Storage
        bucket = storage.bucket()
        blob = bucket.blob(f'student_images/{student_id}.jpg')
        blob.upload_from_file(image_file, content_type='image/jpeg')

        return f"✅ Student {student_name} registered successfully! <a href='/register_student'>Add More</a> | <a href='/'>Go to Dashboard</a>"

    return render_template('register_student.html')



# --------------------- View Students List ------------------------

@app.route('/students')
def students():
    if 'admin' not in session:
        return redirect(url_for('home'))  # Ensure only logged-in admin can access

    students_ref = db.reference('students')
    students_data = students_ref.get()

    students_list = []
    if students_data:
        for student_id, student_info in students_data.items():
            # Generate public URL for the image (assuming storage is set to public access)
            image_url = f"https://firebasestorage.googleapis.com/v0/b/{storage.bucket().name}/o/student_images%2F{student_id}.jpg?alt=media"
            
            students_list.append({
                'student_id': student_id,
                'name': student_info.get('name', ''),
                'mobile_number': student_info.get('mobile_number', ''),
                'email': student_info.get('email', ''),
                'image_url': image_url
            })

    return render_template('view_students.html', students=students_list)

# Attendance History Search Route
@app.route('/attendance_history', methods=['GET', 'POST'])
def attendance_history():
    if 'admin' not in session:
        return redirect('/login')
    
    students_ref = db.reference("students")
    students_data = students_ref.get()
    search_query = request.form.get('search_id') if request.method == 'POST' else ''

    matched_students = {}
    if students_data:
        if search_query:
            for student_id, student_info in students_data.items():
                if search_query in student_id:
                    matched_students[student_id] = student_info
        else:
            matched_students = students_data  # Show all if no search input

    return render_template('attendance_search.html', students=matched_students, search_query=search_query)


# Individual Student Attendance History Route
@app.route('/student_attendance/<student_id>')
def student_attendance(student_id):
    if 'admin' not in session:
        return redirect('/login')
    
    # Fetch attendance and student details from Firebase
    attendance_data = db.reference(f"attendance/{student_id}").get()
    student_info = db.reference(f"students/{student_id}").get()

    # If student not found, handle gracefully
    if not student_info:
        return render_template('student_attendance_history.html', history=[], student=None, student_id=student_id, message="Student not found.")

    history = []
    if attendance_data:
        for date, sessions in attendance_data.items():
            # Get morning and afternoon attendance, default to 'Absent' if not found
            morning = sessions.get('morning', 'Absent')
            afternoon = sessions.get('afternoon', 'Absent')

            # Check if absent for both sessions
            not_present_whole_day = 'Yes' if morning == 'Absent' and afternoon == 'Absent' else 'No'

            # Append record
            history.append({
                'date': date,
                'morning': morning,
                'afternoon': afternoon,
                'not_present_whole_day': not_present_whole_day
            })

    # Sort history by date descending (latest first)
    history.sort(key=lambda x: x['date'], reverse=True)

    return render_template('student_attendance_history.html', 
                           history=history, 
                           student=student_info, 
                           student_id=student_id)


#attendance in the firebase database
@app.route('/api/mark_attendance', methods=['POST'])
def mark_attendance():
    if 'admin' not in session:
        return jsonify({"status": "failed", "message": "Unauthorized"}), 401

    data = request.get_json()
    student_id = data.get('student_id')
    date = data.get('date')  # Should be in YYYY-MM-DD format
    session_type = data.get('session_type')  # 'morning' or 'afternoon'
    status = data.get('status')  # 'Present' or 'Absent'

    if not student_id or not date or not session_type or not status:
        return jsonify({"status": "failed", "message": "Missing data"}), 400

    # Correct way to update without overwriting other sessions or dates

    attendance_ref = db.reference(f'attendance/{student_id}/{date}')
    attendance_ref.update({
        session_type: status
    })

    return jsonify({"status": "success", "message": "Attendance marked successfully!"}), 200


@app.route('/generate_attendance_report')
def generate_attendance_report():
    if 'admin' not in session:
        return redirect(url_for('home'))  # Ensure only admin can generate reports

    # Fetch all students and attendance data from Firebase
    students_ref = db.reference('students')
    students_data = students_ref.get()

    attendance_ref = db.reference('attendance')
    attendance_data = attendance_ref.get()

    # Create a workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance Report"

    # Add header row
    ws.append(["ID", "Name", "Date", "Attendance"])

    # Populate data
    if students_data:
        for student_id, student_info in students_data.items():
            student_name = student_info.get('name', 'Unknown')
            student_attendance = attendance_data.get(student_id, {})

            if student_attendance:
                for date, sessions in student_attendance.items():
                    morning = sessions.get('morning', 'Absent')
                    afternoon = sessions.get('afternoon', 'Absent')

                    # Determine attendance status
                    if morning == 'Present' and afternoon == 'Present':
                        status = 'Present'
                    elif morning == 'Absent' and afternoon == 'Absent':
                        status = 'Absent'
                    else:
                        status = 'Half Day'

                    # Append row to Excel
                    ws.append([student_id, student_name, date, status])
            else:
                # If no attendance records
                ws.append([student_id, student_name, 'No Records', 'No Records'])
    else:
        ws.append(['No Records', 'No Records', 'No Records', 'No Records'])

    # Save the workbook to a BytesIO object
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    # Prepare the filename with date
    filename = f"All_Students_Attendance_Report_{datetime.datetime.now().strftime('%Y-%m-%d')}.xlsx"

    # Return the file for download
    return send_file(output, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')




from flask import render_template, redirect, url_for, session  # Ensure session is imported
from firebase_admin import db

@app.route('/attendance_summary')
def attendance_summary():
    if 'admin' not in session:
        return redirect('/login')  # Secure admin-only route

    # Firebase references
    attendance_ref = db.reference('attendance')
    students_ref = db.reference('students')

    attendance_data = attendance_ref.get()
    students_data = students_ref.get()

    summary_list = []

    if not students_data:
        students_data = {}

    # Loop through all students
    for student_id, student_info in students_data.items():
        total_sessions = 0  # Total sessions (morning + afternoon)
        present_sessions = 0  # Sessions marked 'Present'

        # Fetch attendance records for the student
        student_attendance = attendance_data.get(student_id, {})
        for date, records in student_attendance.items():
            # Each date has up to 2 sessions
            morning_status = records.get('morning')
            afternoon_status = records.get('afternoon')

            if morning_status is not None:
                total_sessions += 1
                if morning_status == 'Present':
                    present_sessions += 1
            if afternoon_status is not None:
                total_sessions += 1
                if afternoon_status == 'Present':
                    present_sessions += 1

        # Calculate absent and percentage
        absent_sessions = total_sessions - present_sessions if total_sessions > 0 else 0
        percentage = (present_sessions / total_sessions) * 100 if total_sessions > 0 else 0.0

        # Append student summary correctly inside loop
        summary_list.append({
            'id': student_id,
            'name': student_info.get('name', 'Unknown'),
            'email': student_info.get('email', 'Not Provided'),
            'total_sessions': total_sessions,
            'present_sessions': present_sessions,
            'absent_sessions': absent_sessions,
            'percentage': round(percentage, 2)
        })

    # Filter students with less than 75% attendance
    low_attendance_students = [student for student in summary_list if student['percentage'] < 75]

    # Render template with all data
    return render_template('attendance_summary.html',
                           summary=summary_list,
                           low_attendance=low_attendance_students)


from flask import jsonify
import smtplib
from email.mime.text import MIMEText

@app.route('/send_alerts', methods=['POST'])
def send_alerts():
    if 'admin' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized access'}), 401

    # Fetch students data again (to ensure latest data, or you can reuse the logic if passing via frontend)
    attendance_ref = db.reference('attendance')
    students_ref = db.reference('students')

    attendance_data = attendance_ref.get()
    students_data = students_ref.get()

    summary_list = []

    for student_id, student_info in students_data.items():
        total_sessions = 0
        present_sessions = 0

        student_attendance = attendance_data.get(student_id, {})
        for date, records in student_attendance.items():
            morning_status = records.get('morning')
            afternoon_status = records.get('afternoon')

            if morning_status is not None:
                total_sessions += 1
                if morning_status == 'Present':
                    present_sessions += 1
            if afternoon_status is not None:
                total_sessions += 1
                if afternoon_status == 'Present':
                    present_sessions += 1

        absent_sessions = total_sessions - present_sessions if total_sessions > 0 else 0
        percentage = (present_sessions / total_sessions) * 100 if total_sessions > 0 else 0.0

        summary_list.append({
            'id': student_id,
            'name': student_info.get('name', 'Unknown'),
            'total_sessions': total_sessions,
            'present_sessions': present_sessions,
            'absent_sessions': absent_sessions,
            'percentage': round(percentage, 2),
            'email': student_info.get('email', 'Not Provided')
        })

    # Filter low attendance students
    low_attendance_students = [student for student in summary_list if student['percentage'] < 75]

    # ==== Sending email logic ====
    sender_email = "attendance.alerts.college@gmail.com"  # Replace with your email
    sender_password = "dscfbtovwcalfjwt"  # App-specific password for security

    subject = "Attendance Alert: Low Attendance Warning"

    # Setup SMTP
    try:
        smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
        smtp_server.starttls()
        smtp_server.login(sender_email, sender_password)

        for student in low_attendance_students:
            recipient_email = student['email']
            if recipient_email == 'Not Provided':
                continue  # Skip if no email available

            message_body = f"""
            Dear {student['name']},

            This is to inform you that your current attendance percentage is {student['percentage']}%.

            Please ensure that you maintain minimum required attendance in upcoming sessions.

            Regards,
            Admin Team
            """

            msg = MIMEText(message_body)
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = recipient_email

            smtp_server.sendmail(sender_email, recipient_email, msg.as_string())

        smtp_server.quit()

        return jsonify({'status': 'success', 'message': 'Alert emails sent successfully'})

    except Exception as e:
        print("Error:", e)
        return jsonify({'status': 'error', 'message': 'Failed to send emails'}), 500


# -------------------------------------------------------------
@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')


@app.route('/start_attendance', methods=['POST'])
def start_attendance():
    global camera_process
    if 'admin' not in session:
        return redirect(url_for('login'))

    if camera_process is None or camera_process.poll() is not None:
        camera_process = subprocess.Popen(["python", "attendance_marking.py"])
        flash("Attendance camera started!")
    else:
        flash("Camera is already running!")

    return redirect(url_for('dashboard'))

# @app.route('/stop_attendance', methods=['POST'])
# def stop_attendance():
#     global camera_process
#     if 'admin' not in session:
#         return redirect(url_for('login'))

#     if camera_process and camera_process.poll() is None:
#         camera_process.terminate()
#         flash("Attendance camera stopped.")
#     else:
#         flash("Camera is not running.")

#     return redirect(url_for('dashboard'))
@app.route('/stop_attendance', methods=['GET','POST'])
def stop_attendance():
    global camera_process
    if 'admin' not in session:
        return redirect(url_for('login'))

    if camera_process and camera_process.poll() is None:
        camera_process.terminate()
        flash("Attendance camera stopped.")
    else:
        flash("Camera is not running.")

    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
