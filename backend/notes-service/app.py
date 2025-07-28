from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# חיבור ל-MongoDB דרך משתנה סביבה
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(mongo_uri)
db = client.notesdb
notes_collection = db.notes

@app.route('/notes', methods=['GET'])
def get_notes():
    notes = []
    for note in notes_collection.find():
        notes.append({
            "id": str(note["_id"]),
            "title": note.get("title", ""),
            "content": note.get("content", "")
        })
    return jsonify(notes), 200

@app.route('/notes', methods=['POST'])
def create_note():
    data = request.json
    new_note = {
        "title": data.get("title", ""),
        "content": data.get("content", "")
    }
    result = notes_collection.insert_one(new_note)
    new_note["id"] = str(result.inserted_id)
    return jsonify(new_note), 201

@app.route('/notes/<note_id>', methods=['PUT'])
def update_note(note_id):
    data = request.json
    result = notes_collection.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": {
            "title": data.get("title", ""),
            "content": data.get("content", "")
        }}
    )
    if result.matched_count:
        return jsonify({"id": note_id, **data}), 200
    return jsonify({"error": "Note not found"}), 404

@app.route('/notes/<note_id>', methods=['DELETE'])
def delete_note(note_id):
    result = notes_collection.delete_one({"_id": ObjectId(note_id)})
    if result.deleted_count:
        return jsonify({"message": "Note deleted"}), 200
    return jsonify({"error": "Note not found"}), 404

@app.route('/')
def home():
    return '''
    <h2>ברוך הבא ל־NoteCloud 📒</h2>
    <p>גש ל־<a href="/notes">/notes</a> כדי לראות את הפתקים.</p>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
