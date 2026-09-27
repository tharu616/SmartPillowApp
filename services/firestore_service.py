import os
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_config import SERVICE_ACCOUNT_FILE

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()


def save_user_profile(user_id, name, email):
    db.collection("users").document(user_id).set({
        "name": name,
        "email": email,
    }, merge=True)


def get_user_profile(user_id):
    doc = db.collection("users").document(user_id).get()
    if doc.exists:
        return doc.to_dict()
    return None


def save_sleep_session(user_id, session_data):
    db.collection("users").document(user_id).collection("sessions").add(session_data)


def get_latest_sleep_session(user_id):
    sessions = (
        db.collection("users")
        .document(user_id)
        .collection("sessions")
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(1)
        .stream()
    )
    for s in sessions:
        return s.to_dict()
    return None


def get_recent_sleep_sessions(user_id, limit=7):
    sessions = (
        db.collection("users")
        .document(user_id)
        .collection("sessions")
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    return [s.to_dict() for s in sessions]


def save_height_preset(user_id, height_value):
    db.collection("users").document(user_id).collection("settings").document("height").set({
        "value": height_value,
    })


def get_height_preset(user_id):
    doc = (
        db.collection("users")
        .document(user_id)
        .collection("settings")
        .document("height")
        .get()
    )
    if doc.exists:
        return doc.to_dict().get("value", 3)
    return 3