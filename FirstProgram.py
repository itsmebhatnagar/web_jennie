from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
import os, json, datetime, pytz, wikipedia

app = Flask(
    __name__,
    static_folder="static",
    static_url_path=""
)

CORS(app)

app.config["JWT_SECRET_KEY"] = "CHANGE_THIS_SECRET"
jwt = JWTManager(app)

USERS_FILE = "users.json"
MEMORY_DIR = "memory"
os.makedirs(MEMORY_DIR, exist_ok=True)

# ---------------- USERS ----------------
def load_users():
    if not os.path.exists(USERS_FILE):
        return {"users": {}}
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

users_db = load_users()

# ---------------- HOME ----------------
@app.route("/")
def home():
    return app.send_static_file("index.html")

# ---------------- AUTH ----------------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username","").strip()
    password = data.get("password","").strip()

    if not username or not password:
        return jsonify({"msg":"Username & password required"}),400

    if username in users_db["users"]:
        return jsonify({"msg":"User already exists"}),400

    role = "master_admin" if not users_db["users"] else "user"

    users_db["users"][username] = {
        "password": generate_password_hash(password),
        "role": role
    }

    save_users(users_db)

    with open(f"{MEMORY_DIR}/{username}.json","w") as f:
        json.dump({"facts":{}, "last_queries":[], "reminders":[]}, f, indent=2)

    return jsonify({"msg":"Registered", "role":role})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username","").strip()
    password = data.get("password","").strip()

    user = users_db["users"].get(username)
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"msg":"Invalid credentials"}),401

    token = create_access_token(identity=username)
    return jsonify({"token":token, "role":user["role"]})

# ---------------- WISH ----------------
@app.route("/api/wish")
def wish():
    ist = pytz.timezone("Asia/Kolkata")
    hour = datetime.datetime.now(ist).hour
    if hour < 12:
        msg = "Good morning! Jennie here."
    elif hour < 18:
        msg = "Good afternoon! Jennie here."
    else:
        msg = "Good evening! Jennie here."
    return jsonify({"response":msg})

# ---------------- MEMORY ----------------
def load_memory(user):
    with open(f"{MEMORY_DIR}/{user}.json") as f:
        return json.load(f)

def save_memory(user, data):
    with open(f"{MEMORY_DIR}/{user}.json","w") as f:
        json.dump(data, f, indent=2)

# ---------------- COMMAND ----------------
@app.route("/api/command", methods=["POST"])
@jwt_required()
def command():
    user = get_jwt_identity()
    mem = load_memory(user)
    query = request.json.get("query","").lower().strip()

    mem["last_queries"].append({
        "query":query,
        "time":datetime.datetime.utcnow().isoformat()
    })
    mem["last_queries"] = mem["last_queries"][-5:]
    save_memory(user, mem)

    if "time" in query:
        return jsonify({"response":datetime.datetime.now().strftime("%I:%M %p")})

    if "open youtube" in query:
        return jsonify({"response":"Opening YouTube","action":"open_youtube"})

    if "open google" in query:
        return jsonify({"response":"Opening Google","action":"open_google"})

    if "open flipkart" in query:
        return jsonify({"response":"Opening Flipkart","action":"open_flipkart"})

    if "open amazon" in query:
        return jsonify({"response":"Opening Amazon","action":"open_amazon"})

    if "open spotify" in query:
        return jsonify({"response":"Opening Spotify","action":"open_spotify"})

    if "wikipedia" in query:
        topic = query.replace("wikipedia","").strip()
        try:
            return jsonify({"response": wikipedia.summary(topic, sentences=1)})
        except:
            return jsonify({"response":"No result found"})

    return jsonify({
        "response":"I’m not sure about that.",
        "action":"search_google",
        "query":query
    })

# ---------------- ADMIN ----------------
@app.route("/api/make-admin", methods=["POST"])
@jwt_required()
def make_admin():
    current = get_jwt_identity()
    if users_db["users"][current]["role"] != "master_admin":
        return jsonify({"msg":"Unauthorized"}),403

    username = request.json.get("username")
    if username not in users_db["users"]:
        return jsonify({"msg":"User not found"}),404

    users_db["users"][username]["role"] = "admin"
    save_users(users_db)
    return jsonify({"msg":f"{username} is now admin"})

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
