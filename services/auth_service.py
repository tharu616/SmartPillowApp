import requests
from firebase_config import API_KEY

SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
LOGIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

def sign_up_user(email, password):
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(SIGNUP_URL, json=payload)
    return response.json()

def sign_in_user(email, password):
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(LOGIN_URL, json=payload)
    return response.json()