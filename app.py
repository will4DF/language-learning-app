from flask import Flask, render_template, request, redirect, session, url_for
import spacy
import textstat
import firebase_admin
from firebase_admin import credentials, auth, firestore
import requests
import os
from dotenv import load_dotenv

# -------------------- Load Environment Variables --------------------
load_dotenv()
API_KEY = os.getenv("FIREBASE_WEB_API_KEY")
print("✅ Firebase API Key loaded successfully")

# -------------------- Firebase Setup --------------------
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()  # Firestore database

# -------------------- Flask Setup --------------------
app = Flask(__name__)
app.secret_key = os.urandom(24)

# -------------------- NLP Setup --------------------
nlp = spacy.load("en_core_web_sm")

# -------------------- Language Logic --------------------
def assess_level(text):
    doc = nlp(text)
    words = [t for t in doc if t.is_alpha]
    if not words:
        return "Unknown"
    avg_word_len = sum(len(t.text) for t in words) / len(words)
    readability = textstat.flesch_reading_ease(text)

    if readability > 70 and avg_word_len < 5:
        return "Beginner"
    elif 50 <= readability <= 70:
        return "Intermediate"
    else:
        return "Advanced"

def recommend_content(level, hobbies):
    base = {
        "Beginner": ["Basic grammar videos", "Simple conversation exercises"],
        "Intermediate": ["Intermediate vocabulary", "Listening practice"],
        "Advanced": ["Advanced writing challenges", "News articles"]
    }
    hobby_suggestions = [f"English lessons about {h.strip()}" for h in hobbies]
    return base.get(level, []) + hobby_suggestions

# -------------------- Authentication --------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}

        response = requests.post(url, json=payload)
        data = response.json()

        if "localId" in data:
            user_id = data["localId"]
            session["user"] = user_id

            # Save user info to Firestore
            db.collection("users").document(user_id).set({
                "email": email,
                "created": firestore.SERVER_TIMESTAMP
            })

            return redirect(url_for("home"))
        else:
            error = data.get("error", {}).get("message", "Signup failed")

    return render_template("signup.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}

        response = requests.post(url, json=payload)
        data = response.json()

        if "idToken" in data:
            session["user"] = data["localId"]
            return redirect(url_for("home"))
        else:
            error = data.get("error", {}).get("message", "Login failed")

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# -------------------- Main Page --------------------
@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    user_id = session["user"]
    user_ref = db.collection("users").document(user_id)

    result = None
    if request.method == "POST":
        text = request.form["text"]
        hobbies = request.form["hobbies"].split(",")
        level = assess_level(text)
        suggestions = recommend_content(level, hobbies)
        result = {"level": level, "suggestions": suggestions}

        # Save progress to Firestore
        user_ref.collection("results").add({
            "text": text,
            "hobbies": hobbies,
            "level": level,
            "timestamp": firestore.SERVER_TIMESTAMP
        })

    # Retrieve previous results for the user
    results = [
        doc.to_dict()
        for doc in user_ref.collection("results")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .stream()
    ]
    return render_template("index.html", result=result, results=results)


# -------------------- Run Server --------------------
if __name__ == "__main__":
    app.run(debug=True)
