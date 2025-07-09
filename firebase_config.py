import firebase_admin
from firebase_admin import credentials, db, storage

# Initialize only once
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://prakruthi-4f54a-default-rtdb.firebaseio.com/',  # ✅ Correct URL
    'storageBucket': 'prakruthi-4f54a.appspot.com'                        # ✅ Correct Bucket
})

# ✅ Now db and bucket are globally available to import
bucket = storage.bucket()

# ✅ Optional: Test connection (you can remove this in production)
ref = db.reference('test')
ref.set({
    'message': 'Firebase connected successfully!'
})

print("✅ Firebase initialized and test data written successfully!")
