"""
MAINN CODE OF OUR PROJECT..................

import cv2
import face_recognition
import numpy as np
import os
import tkinter as tk
from datetime import datetime, time
from firebase_config import db, bucket
import threading

# Directory to temporarily store downloaded images
DOWNLOAD_DIR = "downloaded_images"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Function to download student images from Firebase Storage
def download_images():
    print("📥 Downloading student images from Firebase Storage...")
    blobs = bucket.list_blobs(prefix="student_images/")
    for blob in blobs:
        filename = blob.name.split("/")[-1]
        if filename:  # Avoid empty file names
            blob.download_to_filename(os.path.join(DOWNLOAD_DIR, filename))
            print(f"[+] Downloaded: {filename}")

# Function to load known faces from downloaded images
def load_known_faces():
    known_encodings = []
    known_ids = []

    for filename in os.listdir(DOWNLOAD_DIR):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(DOWNLOAD_DIR, filename)
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)
            if encoding:
                known_encodings.append(encoding[0])
                student_id = os.path.splitext(filename)[0]  # Filename without extension as student_id
                known_ids.append(student_id)
                print(f"[+] Face loaded for ID: {student_id}")
            else:
                print(f"[!] No face found in {filename}, skipping.")

    return known_encodings, known_ids

# Function to check if current time is within allowed attendance windows
def is_within_attendance_window():
    now = datetime.now().time()
    # Define allowed time ranges 555555555555555555555555555555555555555555555555555555555555555555555555555555
    morning_start, morning_end = time(9, 0), time(13, 00)
    afternoon_start, afternoon_end = time(13, 30), time(20, 15)
    # Check if within any allowed slot
    return (morning_start <= now <= morning_end) or (afternoon_start <= now <= afternoon_end)

# Function to get screen resolution
def get_screen_resolution():
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()
    return width, height


# Function to handle real-time face recognition in a separate thread
def recognize_faces(frame, known_faces, known_ids, attendance_marked, screen_width, screen_height):
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_faces, face_encoding)
        face_distances = face_recognition.face_distance(known_faces, face_encoding)
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            student_id = known_ids[best_match_index]

            if student_id not in attendance_marked:
                # Fetch student name
                student_data = db.reference(f'students/{student_id}').get()
                student_name = student_data['name'] if student_data else "Unknown"

                now = datetime.now()
                date_str = now.strftime("%Y-%m-%d")
                current_time = now.time()

                # Determine session time changing111111111111111111111111111111111111111111111111111111111111111
                session = None
                if time(9, 0) <= current_time <= time(13, 00):
                    session = "morning"
                elif time(13, 30) <= current_time <= time(17, 15):
                    session = "afternoon"

                if session:
                    attendance_ref = db.reference(f'attendance/{student_id}/{date_str}/{session}')
                    attendance_ref.set("Present")
                    print(f"[✅] Attendance marked: {student_name} ({student_id}) for {session}")

                attendance_marked.append(student_id)

            # Draw rectangle and label
            top, right, bottom, left = [v * 4 for v in face_location]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 4)
            cv2.putText(frame, student_id, (left, top - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

    # Resize frame to full screen resolution
    output_frame = cv2.resize(frame, (screen_width, screen_height))
    return output_frame




# Function to mark attendance and handle webcam capture
def mark_attendance():
    # Step 1: Download and prepare known faces
    download_images()
    known_faces, known_ids = load_known_faces()

    if not known_faces:
        print("[❌] No valid student images found. Exiting.")
        return

    # Step 2: Initialize Webcam
    video_capture = cv2.VideoCapture(0)
    print("[📷] Webcam started. Press 'q' to quit.")

    # Full screen setup
    window_name = "Attendance System"
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Get screen resolution
    screen_width, screen_height = get_screen_resolution()
    print(f"[🖥️] Screen resolution: {screen_width}x{screen_height}")

    attendance_marked = []  # List to avoid duplicate marking

    while True:
        ret, frame = video_capture.read()
        if not ret:
            continue

        # Check attendance window
        if not is_within_attendance_window():
            frame = cv2.resize(frame, (screen_width, screen_height))
            cv2.putText(frame, "Outside Attendance Time!!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
            cv2.imshow(window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue  # Skip processing if not in allowed time

        # Start a new thread for face recognition to avoid freezing the camera
        recognition_thread = threading.Thread(target=recognize_faces, args=(frame, known_faces, known_ids, attendance_marked, screen_width, screen_height))
        recognition_thread.start()

        # Display the updated frame
        recognition_thread.join()  # Wait for the recognition thread to finish
        cv2.imshow(window_name, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release and cleanup
    video_capture.release()
    cv2.destroyAllWindows()
    print("[✅] Attendance session ended.")

# Main Entry
if __name__ == "__main__":
    mark_attendance()




#using the MTCNN......................

"""
import cv2
import face_recognition
import numpy as np
import os
import tkinter as tk
from datetime import datetime, time
from firebase_config import db, bucket
import threading
from mtcnn import MTCNN

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

DOWNLOAD_DIR = "downloaded_images"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Download images from Firebase
def download_images():
    print("📥 Downloading student images from Firebase Storage...")
    blobs = bucket.list_blobs(prefix="student_images/")
    for blob in blobs:
        filename = blob.name.split("/")[-1]
        if filename:
            blob.download_to_filename(os.path.join(DOWNLOAD_DIR, filename))
            print(f"[+] Downloaded: {filename}")

# Load and encode known faces
def load_known_faces():
    known_encodings = []
    known_ids = []

    for filename in os.listdir(DOWNLOAD_DIR):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(DOWNLOAD_DIR, filename)
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)
            if encoding:
                known_encodings.append(encoding[0])
                student_id = os.path.splitext(filename)[0]
                known_ids.append(student_id)
                print(f"[+] Face loaded for ID: {student_id}")
            else:
                print(f"[!] No face found in {filename}, skipping.")

    return known_encodings, known_ids

# Check time window
def is_within_attendance_window():
    now = datetime.now().time()
    morning_start, morning_end = time(9, 0), time(13, 0)
    afternoon_start, afternoon_end = time(13, 30), time(20, 55)
    return (morning_start <= now <= morning_end) or (afternoon_start <= now <= afternoon_end)

# Screen resolution
def get_screen_resolution():
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()
    return width, height

# Face recognition logic
def recognize_faces(frame, known_faces, known_ids, attendance_marked, screen_width, screen_height, detector):
    results = detector.detect_faces(frame)
    tolerance = 0.50 # Stricter threshold for higher accuracy

    for result in results:
        x, y, w, h = result['box']
        face = frame[y:y+h, x:x+w]
        rgb_face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        face_encoding = face_recognition.face_encodings(rgb_face)

        if face_encoding:
            face_encoding = face_encoding[0]
            matches = face_recognition.compare_faces(known_faces, face_encoding, tolerance=tolerance)
            face_distances = face_recognition.face_distance(known_faces, face_encoding)
            best_match_index = np.argmin(face_distances)

            print(f"Face distances: {face_distances}")  # Debugging line

            if face_distances[best_match_index] < tolerance and matches[best_match_index]:
                student_id = known_ids[best_match_index]

                if student_id not in attendance_marked:
                    student_data = db.reference(f'students/{student_id}').get()
                    student_name = student_data['name'] if student_data else "Unknown"

                    now = datetime.now()
                    date_str = now.strftime("%Y-%m-%d")
                    current_time = now.time()

                    session = None
                    if time(9, 0) <= current_time <= time(13, 0):
                        session = "morning"
                    elif time(13, 30) <= current_time <= time(20, 55):
                        session = "afternoon"

                    if session:
                        attendance_ref = db.reference(f'attendance/{student_id}/{date_str}/{session}')
                        attendance_ref.set("Present")
                        print(f"[✅] Attendance marked: {student_name} ({student_id}) for {session}")

                    attendance_marked.append(student_id)

                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 4)
                cv2.putText(frame, student_id, (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 4)
                cv2.putText(frame, "Unknown", (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

    return cv2.resize(frame, (screen_width, screen_height))

# Main attendance logic
def mark_attendance():
    download_images()
    known_faces, known_ids = load_known_faces()

    if not known_faces:
        print("[❌] No valid student images found. Exiting.")
        return

    video_capture = cv2.VideoCapture(0)
    print("[📷] Webcam started. Press 'q' to quit.")

    window_name = "Attendance System"
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    screen_width, screen_height = get_screen_resolution()
    print(f"[🖥️] Screen resolution: {screen_width}x{screen_height}")

    attendance_marked = []
    processed_frame = None
    recognition_thread = None
    detector = MTCNN()

    def recognition_worker(frame_copy):
        nonlocal processed_frame
        processed_frame = recognize_faces(frame_copy, known_faces, known_ids, attendance_marked, screen_width, screen_height, detector)

    while True:
        ret, frame = video_capture.read()
        if not ret:
            continue

        if not is_within_attendance_window():
            frame = cv2.resize(frame, (screen_width, screen_height))
            cv2.putText(frame, "Outside Attendance Time!!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
            cv2.imshow(window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        if recognition_thread is None or not recognition_thread.is_alive():
            frame_copy = frame.copy()
            recognition_thread = threading.Thread(target=recognition_worker, args=(frame_copy,))
            recognition_thread.start()

        display_frame = processed_frame if processed_frame is not None else cv2.resize(frame, (screen_width, screen_height))
        cv2.imshow(window_name, display_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    print("[✅] Attendance session ended.")

# Entry point
if __name__ == "__main__":
    mark_attendance()
