from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
import os
import datetime
import wikipedia
import pytz
import json
import bcrypt
import re

# ---------------- APP SETUP ----------------

app = Flask(__name__, static_folder="static")
CORS(app)

app.config["JWT_SECRET_KEY"] = "change-this-secret-key"
jwt = JWTManager(app)

# ---------------- USER SYSTEM ----------------

USERS_FILE = "users.json"
MEMORY_DIR = "memory"

if not os.path.exists(MEMORY_DIR):
    os.makedirs(MEMORY_DIR)


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {"users": {}}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())


# ---------------- MEMORY (PER USER) ----------------

def load_user_memory(user_id):
    path = f"{MEMORY_DIR}/{user_id}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {
        "facts": {},
        "last_queries": [],
        "reminders": []
    }


def save_user_memory(user_id, memory):
    with open(f"{MEMORY_DIR}/{user_id}.json", "w") as f:
        json.dump(memory, f, indent=2)


# ---------------- AUTH ROUTES ----------------

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "Missing fields"}), 400

    users = load_users()

    if username in users["users"]:
        return jsonify({"msg": "User already exists"}), 400

    users["users"][username] = {
        "password": hash_password(password),
        "created_at": datetime.datetime.now().isoformat()
    }

    save_users(users)
    return jsonify({"msg": "User registered successfully"})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")

    users = load_users()

    if username not in users["users"]:
        return jsonify({"msg": "Invalid credentials"}), 401

    if not check_password(password, users["users"][username]["password"]):
        return jsonify({"msg": "Invalid credentials"}), 401

    token = create_access_token(identity=username)
    return jsonify({"access_token": token})


# ---------------- BASIC ROUTES ----------------

@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/api/wish", methods=["GET"])
@jwt_required()
def wish_me():
    ist = pytz.timezone("Asia/Kolkata")
    hour = datetime.datetime.now(ist).hour

    if 0 <= hour < 12:
        wish = "Good morning! Jennie here ☀️"
    elif 12 <= hour < 18:
        wish = "Good afternoon! Jennie here 🌤️"
    else:
        wish = "Good evening! Jennie here 🌙"

    return jsonify({"response": wish})


# ---------------- COMMAND HANDLER ----------------

@app.route("/api/command", methods=["POST"])
@jwt_required()
def api_command():
    user_id = get_jwt_identity()
    memory = load_user_memory(user_id)

    data = request.get_json(force=True)
    query = data.get("query", "").lower().strip()

    # save last queries
    memory["last_queries"].append({
        "query": query,
        "time": datetime.datetime.now().isoformat()
    })
    memory["last_queries"] = memory["last_queries"][-5:]

    # ---- COMMANDS ----

    if "time" in query:
        now = datetime.datetime.now().strftime("%I:%M %p")
        response = f"The current time is {now}"

    elif "open youtube" in query:
        response = "Opening YouTube..."
        save_user_memory(user_id, memory)
        return jsonify({"response": response, "action": "open_youtube"})

    elif "open google" in query:
        response = "Opening Google..."
        save_user_memory(user_id, memory)
        return jsonify({"response": response, "action": "open_google"})

    elif "wikipedia" in query:
        topic = query.replace("wikipedia", "").strip()
        try:
            result = wikipedia.summary(topic, sentences=1)
            response = f"According to Wikipedia: {result}"
        except Exception:
            response = "Sorry, I couldn’t find that on Wikipedia."

    elif query.startswith("remember"):
        fact = query.replace("remember", "").strip()
        key = f"fact_{len(memory['facts']) + 1}"
        memory["facts"][key] = fact
        response = f"I'll remember: {fact}"

    elif "what do i like" in query or "what did i tell you" in query:
        facts = list(memory["facts"].values())
        response = "You told me: " + "; ".join(facts) if facts else "You haven't told me anything yet."

    elif query.startswith("remind me to"):
        m = re.search(r"remind me to (.+) in (\d+)\s*(minute|minutes|hour|hours)", query)
        if m:
            text = m.group(1)
            num = int(m.group(2))
            unit = m.group(3)
            seconds = num * 60
            if unit.startswith("hour"):
                seconds *= 60

            time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            memory["reminders"].append({
                "text": text,
                "time": time.isoformat(),
                "notified": False
            })
            response = f"Reminder set for {num} {unit} from now."
        else:
            response = "Sorry, I couldn't understand the reminder."

    else:
        save_user_memory(user_id, memory)
        return jsonify({
            "response": "I'm not sure about that. I can search Google for you.",
            "action": "search_google",
            "query": query
        })

    save_user_memory(user_id, memory)
    return jsonify({"response": response})


# ---------------- REMINDERS ----------------

@app.route("/api/reminders/due", methods=["GET"])
@jwt_required()
def due_reminders():
    user_id = get_jwt_identity()
    memory = load_user_memory(user_id)

    now = datetime.datetime.now()
    due = []
    changed = False

    for r in memory["reminders"]:
        if not r["notified"]:
            dt = datetime.datetime.fromisoformat(r["time"])
            if dt <= now:
                due.append(r)
                r["notified"] = True
                changed = True

    if changed:
        save_user_memory(user_id, memory)

    return jsonify(due)


# ---------------- RUN ----------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
