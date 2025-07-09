import firebase_admin
from firebase_admin import credentials, db, storage
import os

# Initialize Firebase (use existing serviceAccountKey.json)
cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://prakruthi-4f54a-default-rtdb.firebaseio.com/',
    'storageBucket': 'prakruthi-4f54a.appspot.com'
})

# ---------- Function to Register a Student ----------

def register_student(student_id, name, image_path):
    # 1. Upload details to Realtime Database
    ref = db.reference('students')
    student_ref = ref.child(student_id)
    student_ref.set({
        'name': name,
        'image': f"{student_id}.jpg"  # Storing image filename as reference
    })
    print(f"✅ Student {name} data uploaded to Realtime Database!")

    # 2. Upload image to Storage
    bucket = storage.bucket()
    blob = bucket.blob(f"students/{student_id}.jpg")  # Save inside "students" folder
    blob.upload_from_filename(image_path)
    print(f"✅ Image {image_path} uploaded to Firebase Storage!")

# ---------- Main Part to Take Input ----------

if __name__ == "__main__":
    student_id = input("Enter Student ID: ")
    name = input("Enter Student Name: ")
    image_path = input("Enter path to Student's Image: ")

    # Check if image exists
    if not os.path.exists(image_path):
        print("❌ Image file does not exist! Please check the path.")
    else:
        register_student(student_id, name, image_path)

