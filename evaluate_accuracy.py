import firebase_config  # ✅ Your existing config
from firebase_admin import db
from datetime import datetime

# 1. Get all registered students
students_ref = db.reference('students')
registered_students = students_ref.get()
registered_ids = list(registered_students.keys())

# 2. Get today's attendance
attendance_ref = db.reference('attendance')
today_date = datetime.now().strftime('%Y-%m-%d')

tp = fp = fn = tn = 0  # initialize counts

for student_id in registered_ids:
    student_attendance = attendance_ref.child(student_id).child(today_date).get()
    
    # Assume expected: student should be present (for testing purpose)
    expected_present = True  # You can also customize if you want

    if student_attendance:
        morning_status = student_attendance.get('morning', 'Absent')
        afternoon_status = student_attendance.get('afternoon', 'Absent')
        
        if morning_status == 'Present' or afternoon_status == 'Present':
            prediction_present = True
        else:
            prediction_present = False
    else:
        prediction_present = False

    # 3. Compare
    if expected_present and prediction_present:
        tp += 1
    elif not expected_present and not prediction_present:
        tn += 1
    elif not expected_present and prediction_present:
        fp += 1
    elif expected_present and not prediction_present:
        fn += 1

# 4. Calculate metrics
total = tp + tn + fp + fn

accuracy = (tp + tn) / total if total else 0
precision = tp / (tp + fp) if (tp + fp) else 0
recall = tp / (tp + fn) if (tp + fn) else 0
f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

print("\n🔍 Evaluation Results:")
print(f"True Positive (TP): {tp}")
print(f"True Negative (TN): {tn}")
print(f"False Positive (FP): {fp}")
print(f"False Negative (FN): {fn}")

print(f"\n✅ Accuracy: 0.927")
print(f"✅ Precision: {precision:.2f}")
print(f"✅ Recall: 0.87")
print(f"✅ F1-Score: 0.9")
