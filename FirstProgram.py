from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import datetime
import wikipedia
import pytz
import json

app = Flask(__name__)
CORS(app)

# ---------- TIME GREETING ----------
@app.route("/api/wish", methods=["GET"])
def wish_me():
    ist = pytz.timezone("Asia/Kolkata")
    hour = datetime.datetime.now(ist).hour

    if 0 <= hour < 12:
        wish = "Good morning! Jennie here. How can I help you today?"
    elif 12 <= hour < 18:
        wish = "Good afternoon! Jennie here. How can I assist you?"
    else:
        wish = "Good evening! Jennie here. How can I assist you tonight?"

    return jsonify({"response": wish})


@app.route("/")
def home():
    return "Jennie backend is running!"


# ---------- MEMORY MANAGEMENT ----------
def load_memory():
    if os.path.exists("memory.json"):
        with open("memory.json", "r") as f:
            return json.load(f)
    return {"facts": {}, "last_queries": [], "reminders": []}


def save_memory(memory):
    with open("memory.json", "w") as f:
        json.dump(memory, f, indent=2)


memory = load_memory()


@app.route("/api/memory", methods=["GET"])
def get_memory():
    return jsonify(memory)


@app.route("/api/memory", methods=["POST"])
def set_memory():
    data = request.get_json(force=True)
    key = data.get("key")
    value = data.get("value")
    if not key:
        return jsonify({"response": "Invalid request"}), 400
    memory["facts"][key] = value
    save_memory(memory)
    return jsonify({"response": f"Saved {key}."})


# ---------- CHAT HISTORY ----------
@app.route("/api/last_queries", methods=["GET"])
def last_queries():
    return jsonify(memory.get("last_queries", []))


# ---------- REMINDER SYSTEM ----------
@app.route("/api/reminders", methods=["POST"])
def add_reminder():
    data = request.get_json(force=True)
    text = data.get("text")
    time_str = data.get("time")
    if not text or not time_str:
        return jsonify({"response": "Invalid reminder data"}), 400
    try:
        dt = datetime.datetime.fromisoformat(time_str)
    except Exception:
        return jsonify({"response": "Invalid datetime format"}), 400
    rem = {"text": text, "time": dt.isoformat(), "notified": False}
    memory.setdefault("reminders", []).append(rem)
    save_memory(memory)
    return jsonify({"response": "Reminder saved."})


@app.route("/api/reminders/due", methods=["GET"])
def due_reminders():
    now = datetime.datetime.now()
    due = []
    changed = False
    for r in memory.get("reminders", []):
        if not r.get("notified"):
            dt = datetime.datetime.fromisoformat(r["time"])
            if dt <= now:
                due.append(r)
                r["notified"] = True
                changed = True
    if changed:
        save_memory(memory)
    return jsonify(due)


# ---------- MAIN COMMAND HANDLER ----------
@app.route("/api/command", methods=["POST"])
def api_command():
    data = request.get_json(force=True)
    query = data.get("query", "").lower().strip()

    # store last 5 queries
    last = memory.get("last_queries", [])
    last.append({"query": query, "time": datetime.datetime.now().isoformat()})
    memory["last_queries"] = last[-5:]
    save_memory(memory)

    # ----- Predefined commands -----
    if "time" in query:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return jsonify({"response": f"The current time is {now}"})

    elif "open youtube" in query:
        return jsonify({"response": "Opening YouTube...", "action": "open_youtube"})

    elif "open google" in query:
        return jsonify({"response": "Opening Google...", "action": "open_google"})

    elif "open flipkart" in query:
        return jsonify({"response": "Opening Flipkart...", "action": "open_flipkart"})

    elif "open amazon" in query:
        return jsonify({"response": "Opening Amazon...", "action": "open_amazon"})

    elif "open helper" in query or "open chatgpt" in query:
        return jsonify({"response": "Opening ChatGPT...", "action": "open_chatgpt"})

    elif "open spotify" in query:
        return jsonify({"response": "Opening Spotify...", "action": "open_spotify"})

    elif "wikipedia" in query:
        topic = query.replace("wikipedia", "").strip()
        try:
            result = wikipedia.summary(topic, sentences=1)
            return jsonify({"response": f"According to Wikipedia: {result}"})
        except Exception:
            return jsonify({"response": "Sorry, I couldn’t find that on Wikipedia."})

    elif "my name is" in query:
        name = query.split("my name is")[-1].strip().capitalize()
        memory["name"] = name
        save_memory(memory)
        return jsonify({"response": f"Nice to meet you, {name}!"})

    elif "what is my name" in query:
        name = memory.get("name", "I don't know your name yet.")
        return jsonify({"response": name})

    elif query.startswith("remember that ") or query.startswith("remember "):
        fact = query.replace("remember that", "").replace("remember", "").strip()
        key = f"fact_{len(memory['facts'])+1}"
        memory["facts"][key] = fact
        save_memory(memory)
        return jsonify({"response": f"I'll remember: {fact}"})

    elif "what do i like" in query or "what did i tell you" in query:
        facts = list(memory["facts"].values())
        if not facts:
            return jsonify({"response": "I don't have any saved facts yet."})
        return jsonify({"response": "You told me: " + "; ".join(facts)})

    elif query.startswith("remind me to"):
        import re
        m = re.search(r"remind me to (.+) in (\d+)\s*(minute|minutes|hour|hours)", query)
        if m:
            text = m.group(1)
            num = int(m.group(2))
            unit = m.group(3)
            seconds = num * 60
            if unit.startswith("hour"):
                seconds *= 60
            time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            memory.setdefault("reminders", []).append({
                "text": text, "time": time.isoformat(), "notified": False
            })
            save_memory(memory)
            return jsonify({"response": f"Reminder set for {num} {unit} from now."})

    # ---------- Smart Search Fallback ----------
    else:
        return jsonify({
            "response": "I’m not sure about that. I can search the web for you.",
            "action": "search_google",
            "query": query
        })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
