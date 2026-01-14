from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity, get_jwt
)
import os, json, datetime, bcrypt, pytz, wikipedia, re

app = Flask(__name__, static_folder="static")
CORS(app)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-secret")
jwt = JWTManager(app)

USERS_FILE = "users.json"
MEMORY_DIR = "memory"
os.makedirs(MEMORY_DIR, exist_ok=True)

# ---------- HELPERS ----------

def load_users():
    if os.path.exists(USERS_FILE):
        return json.load(open(USERS_FILE))
    return {"users": {}}

def save_users(data):
    json.dump(data, open(USERS_FILE, "w"), indent=2)

def hash_pw(p): return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
def check_pw(p, h): return bcrypt.checkpw(p.encode(), h.encode())

def load_mem(uid):
    path = f"{MEMORY_DIR}/{uid}.json"
    return json.load(open(path)) if os.path.exists(path) else {
        "facts": {}, "last_queries": [], "reminders": []
    }

def save_mem(uid, mem):
    json.dump(mem, open(f"{MEMORY_DIR}/{uid}.json", "w"), indent=2)

# ---------- AUTH ----------

@app.route("/api/register", methods=["POST"])
def register():
    d = request.json
    users = load_users()

    role = "master_admin" if not users["users"] else "user"

    users["users"][d["username"]] = {
        "password": hash_pw(d["password"]),
        "role": role,
        "created": datetime.datetime.now().isoformat()
    }
    save_users(users)
    return jsonify({"msg": f"Registered as {role}"})


@app.route("/api/login", methods=["POST"])
def login():
    d = request.json
    users = load_users()["users"]

    if d["username"] not in users:
        return jsonify({"msg": "Invalid"}), 401

    u = users[d["username"]]
    if not check_pw(d["password"], u["password"]):
        return jsonify({"msg": "Invalid"}), 401

    token = create_access_token(
        identity=d["username"],
        additional_claims={"role": u["role"]}
    )
    return jsonify({"access_token": token, "role": u["role"]})

# ---------- ADMIN APIs ----------

@app.route("/api/admin/users", methods=["GET"])
@jwt_required()
def list_users():
    role = get_jwt()["role"]
    if role not in ["admin", "master_admin"]:
        return jsonify({"msg": "Forbidden"}), 403
    return jsonify(load_users()["users"])

@app.route("/api/admin/make-admin", methods=["POST"])
@jwt_required()
def make_admin():
    claims = get_jwt()
    if claims["role"] != "master_admin":
        return jsonify({"msg": "Only master admin"}), 403

    username = request.json["username"]
    users = load_users()
    if username in users["users"]:
        users["users"][username]["role"] = "admin"
        save_users(users)
        return jsonify({"msg": f"{username} is admin"})
    return jsonify({"msg": "User not found"}), 404

# ---------- ASSISTANT ----------

@app.route("/api/wish")
@jwt_required()
def wish():
    h = datetime.datetime.now(pytz.timezone("Asia/Kolkata")).hour
    return jsonify({"response":
        "Good morning" if h < 12 else "Good evening"
    })

@app.route("/api/command", methods=["POST"])
@jwt_required()
def command():
    user = get_jwt_identity()
    mem = load_mem(user)
    q = request.json["query"].lower()

    mem["last_queries"].append(q)
    mem["last_queries"] = mem["last_queries"][-5:]

    if "time" in q:
        r = datetime.datetime.now().strftime("%I:%M %p")
    elif q.startswith("remember"):
        mem["facts"][f"fact{len(mem['facts'])+1}"] = q
        r = "Saved"
    else:
        r = "I can search this for you"

    save_mem(user, mem)
    return jsonify({"response": r})

@app.route("/api/reminders/due")
@jwt_required()
def reminders():
    mem = load_mem(get_jwt_identity())
    return jsonify(mem["reminders"])

# ---------- RUN ----------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
