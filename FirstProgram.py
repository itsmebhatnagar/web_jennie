from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import datetime
import wikipedia
import pytz

app = Flask(__name__)
CORS(app)

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

@app.route("/api/command", methods=["POST"])
def api_command():
    data = request.get_json(force=True)
    query = data.get("query", "").lower()

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

    elif "open helper" in query:
        return jsonify({"response": "Opening Chatgpt...", "action": "open_chatgpt"})

    elif "open spotify" in query:
        return jsonify({"response": "Opening spotify...", "action": "open_spotify"})

    elif "wikipedia" in query:
        topic = query.replace("wikipedia", "").strip()
        try:
            result = wikipedia.summary(topic, sentences=1)
            return jsonify({"response": f"According to Wikipedia: {result}"})
        except Exception:
            return jsonify({"response": "Sorry, I couldn’t find that on Wikipedia."})

    else:
        return jsonify({"response": "Sorry, I didn’t understand that command."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
