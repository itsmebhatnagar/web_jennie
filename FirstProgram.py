from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import datetime
import wikipedia

app = Flask(__name__)
CORS(app)

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
