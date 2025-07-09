import firebase_config  # ✅ Import to initialize Firebase
from firebase_admin import db
from datetime import datetime, timedelta

# ✅ Fetch student list
students_ref = db.reference('students')
students = students_ref.get()

# ✅ Set date range from 2025-04-15 to today
start_date = datetime.strptime('2025-04-15', '%Y-%m-%d')
end_date = datetime.now()

# ✅ Attendance reference
attendance_ref = db.reference('attendance')

# ✅ Loop through each date from start_date to end_date
current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime('%Y-%m-%d')
    print(f"\n📅 Checking attendance for date: {date_str}")

    # ✅ Loop through each student
    for student_id in students:
        print(f"🔍 Checking attendance for student: {student_id}")
        student_attendance_ref = attendance_ref.child(student_id).child(date_str)
        student_attendance = student_attendance_ref.get()

        # If attendance not marked yet, initialize empty dict
        if not student_attendance:
            student_attendance = {}

        # Check and mark 'morning' attendance
        if 'morning' not in student_attendance:
            print(f"⚠️ Marking morning absent for {student_id} on {date_str}")
            student_attendance_ref.update({'morning': 'Absent'})
        else:
            print(f"✅ Morning attendance already marked for {student_id} on {date_str}")

        # Check and mark 'afternoon' attendance
        if 'afternoon' not in student_attendance:
            print(f"⚠️ Marking afternoon absent for {student_id} on {date_str}")
            student_attendance_ref.update({'afternoon': 'Absent'})
        else:
            print(f"✅ Afternoon attendance already marked for {student_id} on {date_str}")

    current_date += timedelta(days=1)  # ✅ Move to next date

print("\n✅ Auto attendance marking completed for all dates and students.")
