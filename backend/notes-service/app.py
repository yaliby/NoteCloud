from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime
import bcrypt
import os

app = Flask(__name__)

# קישור למסד הנתונים
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/CloudeNoteDB")
mongo = PyMongo(app)
users_collection = mongo.db.UsersInfo


def normalize_email(s: str) -> str:
    return (s or "").strip().lower()


# המרת ObjectId ל-string בתשובות
def serialize_user(user):
    user["_id"] = str(user["_id"])
    return user

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "NoteCloud API is live ✅"})

# הרשמת משתמש חדש
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = normalize_email(data.get('email'))
    password = data.get("password")
    name = data.get("name")

    if not email or not password or not name:
        return jsonify({"error": "Missing fields"}), 400

    # בדיקת כפילות
    if users_collection.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 409

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    user = {
        "email": email,
        "password": hashed_pw,
        "name": name,
        "joined": datetime.utcnow().isoformat(),
        "notes": []
    }

    result = users_collection.insert_one(user)
    return jsonify({"message": "User created", "user_id": str(result.inserted_id)}), 201

# הוספת פתק למשתמש
@app.route("/users/<user_id>/notes", methods=["POST"])
def add_note(user_id):
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return jsonify({"error": "Missing fields"}), 400

    note = {
        "id": str(ObjectId()),
        "title": title,
        "content": content,
        "created": datetime.utcnow().isoformat()
    }

    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"notes": note}}
    )

    if result.modified_count == 0:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"message": "Note added", "note": note}), 201

# שליפת הפתקים של משתמש
@app.route("/users/<user_id>/notes", methods=["GET"])
def get_notes(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"notes": user.get("notes", [])})

# התחברות משתמש קיים
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = normalize_email(data.get('email'))
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # בדיקת התאמת סיסמה
    if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return jsonify({"error": "Incorrect password"}), 401

    return jsonify({
        "message": "Login successful",
        "user_id": str(user["_id"]),
        "name": user["name"]
    }), 200

# הרצה
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
