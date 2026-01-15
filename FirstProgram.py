from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import wikipedia
import pytz
import os
import json

app = Flask(__name__, static_folder="static")
CORS(app)

# ---------------- HOME (SERVE FRONTEND) ----------------
@app.route("/")
def home():
    return app.send_static_file("index.html")


# ---------------- TIME GREETING ----------------
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


# ---------------- MEMORY ----------------
def load_memory():
    if os.path.exists("memory.json"):
        with open("memory.json", "r") as f:
            return json.load(f)
    return {"last_queries": [], "wishes": []}

def save_memory(mem):
    with open("memory.json", "w") as f:
        json.dump(mem, f, indent=2)

memory = load_memory()


# ---------------- COMMAND HANDLER ----------------
@app.route("/api/command", methods=["POST"])
def api_command():
    data = request.get_json(force=True)
    query = data.get("query", "").lower().strip()

    memory["last_queries"].append({
        "query": query,
        "time": datetime.datetime.now().isoformat()
    })
    memory["last_queries"] = memory["last_queries"][-5:]
    save_memory(memory)

    if "time" in query:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return jsonify({"response": f"The current time is {now}"})

    elif "open youtube" in query:
        return jsonify({"response": "Opening YouTube...", "action": "open_youtube"})

    elif "open google" in query:
        return jsonify({"response": "Opening Google...", "action": "open_google"})

    elif "open amazon" in query:
        return jsonify({"response": "Opening Amazon...", "action": "open_amazon"})

    elif "open flipkart" in query:
        return jsonify({"response": "Opening Flipkart...", "action": "open_flipkart"})

    elif "open spotify" in query:
        return jsonify({"response": "Opening Spotify...", "action": "open_spotify"})

    elif "play" in query and "on spotify" in query:
        # Extract song name from "play [song name] on spotify"
        import urllib.parse
        song_name = query.replace("play", "").replace("on spotify", "").strip()
        if song_name:
            # Create Spotify URI that can directly play songs (requires Spotify app)
            # Also provide web fallback
            encoded_song = urllib.parse.quote(song_name)
            spotify_uri = f"spotify:search:{encoded_song}"
            spotify_web_url = f"https://open.spotify.com/search/{encoded_song}"
            
            return jsonify({
                "response": f"Playing {song_name} on Spotify...",
                "action": "play_spotify",
                "uri": spotify_uri,
                "url": spotify_web_url,
                "song": song_name
            })
        else:
            return jsonify({"response": "Please specify a song name. For example: 'play Shape of You on Spotify'"})

    elif "search" in query and "on youtube" in query:
        # Extract search term from "search [term] on youtube"
        import urllib.parse
        search_term = query.replace("search", "").replace("on youtube", "").strip()
        if search_term:
            # Create YouTube search URL
            encoded_term = urllib.parse.quote(search_term)
            youtube_url = f"https://www.youtube.com/results?search_query={encoded_term}"
            
            return jsonify({
                "response": f"Searching for {search_term} on YouTube...",
                "action": "search_youtube",
                "url": youtube_url,
                "term": search_term
            })
        else:
            return jsonify({"response": "Please specify what to search. For example: 'search Ed Sheeran on YouTube'"})

    elif "wikipedia" in query:
        topic = query.replace("wikipedia", "").strip()
        try:
            result = wikipedia.summary(topic, sentences=1)
            return jsonify({"response": result})
        except:
            return jsonify({"response": "Sorry, I couldn't find that on Wikipedia."})

    elif "wish me" in query or "make a wish" in query:
        ist = pytz.timezone("Asia/Kolkata")
        hour = datetime.datetime.now(ist).hour
        
        if 0 <= hour < 12:
            greeting = "Good morning"
        elif 12 <= hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good night"
        
        return jsonify({"response": f"{greeting}! What would you like to wish for today?"})

    elif query.startswith("i wish ") or query.startswith("my wish is "):
        if query.startswith("i wish "):
            wish = query.replace("i wish ", "").strip()
        else:
            wish = query.replace("my wish is ", "").strip()
        
        memory["wishes"].append({
            "wish": wish,
            "time": datetime.datetime.now().isoformat()
        })
        save_memory(memory)
        return jsonify({"response": f"I've saved your wish: '{wish}'. May all your dreams come true!"})

    elif "show my wishes" in query or "my wishes" in query:
        if memory["wishes"]:
            wishes_list = [f"• {w['wish']}" for w in memory["wishes"]]
            return jsonify({"response": f"Your wishes:\n" + "\n".join(wishes_list)})
        else:
            return jsonify({"response": "You haven't made any wishes yet."})

    else:
        return jsonify({
            "response": "I'm not sure about that. I can search the web for you.",
            "action": "search_google",
            "query": query
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
