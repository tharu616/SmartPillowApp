from firebase_admin import firestore
import services.firestore_service  # noqa: F401  (Firebase app initialise වෙන්න)


def _doc(user_id):
    return (
        firestore.client()
        .collection("users")
        .document(user_id)
        .collection("settings")
        .document("alarms")
    )


def load_alarms(user_id):
    if not user_id:
        return []
    try:
        d = _doc(user_id).get()
        if d.exists:
            return list(d.to_dict().get("items", []))
    except Exception as e:
        print("Load alarms failed:", e)
    return []


def save_alarms(user_id, items):
    if not user_id:
        return
    try:
        _doc(user_id).set({"items": items})
    except Exception as e:
        print("Save alarms failed:", e)