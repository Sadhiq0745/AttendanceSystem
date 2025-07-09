import firebase_config  # ✅ Your existing Firebase connection
from firebase_admin import db
from datetime import datetime, timedelta

# ✅ Fetch all students
students_ref = db.reference('students')
students = students_ref.get()

# ✅ Set the date range to delete (March 10 to March 12)
start_date = datetime.strptime('2025-03-10', '%Y-%m-%d')
end_date = datetime.strptime('2025-03-12', '%Y-%m-%d')

# ✅ Attendance reference
attendance_ref = db.reference('attendance')

# ✅ Loop through each date in the range
current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime('%Y-%m-%d')
    print(f"\n🗑️ Deleting attendance for date: {date_str}")

    # ✅ Loop through each student and delete attendance for that date
    for student_id in students:
        print(f"❌ Removing attendance of {student_id} for {date_str}")
        attendance_ref.child(student_id).child(date_str).delete()

    current_date += timedelta(days=1)  # ✅ Move to next da~te

print("\n✅ Successfully removed attendance records from 2025-03-10 to 2025-03-12 for all students.")
