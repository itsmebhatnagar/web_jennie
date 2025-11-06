from click import command
import pyttsx3 #pip install pyttsx3
import speech_recognition as sr #pip install speechRecognition
from flask import Flask, send_from_directory
import datetime
import webbrowser
import os
import wikipedia
import pywhatkit
import pyautogui

#Intialize Voice Assistant
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
# print(voices[1].id)
engine.setProperty('voice', voices[0].id)

app = Flask(__name__, static_folder="static", static_url_path="/static")
ALLOWED_EXT = {"wav", "webm", "mp3", "m4a", "ogg"}

def speak(audio):
    engine.say(audio)
    engine.runAndWait()
    
@app.route("/")
def index():
    return send_from_directory("static", "jennie.html")

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning! Jennie in your service. How can I help you?")

    elif hour>=12 and hour<18:
        speak("Good Afternoon! Jennie in your service. How can I help you?")   

    else:
        speak("Good Evening! Jennie in your service. How can I help you?")         

def takeCommand():
    #It takes microphone input from the user and returns string output

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")    
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")

    except Exception as e:
        # print(e)    
        print("Say that again please...")  
        return "None"
    return query

def wikipedia_search(query):
    speak("Searching Wikipedia...")
    query = query.replace("wikipedia", "")
    try:
        results = wikipedia.summary(query, sentences=2)
        print(results)
        speak("According to Wikipedia...")
        speak(results)
    except wikipedia.exceptions.DisambiguationError:
        speak("There are multiple results. Please be more specific.")
    except wikipedia.exceptions.PageError:
        speak("I could not find any results for that topic.")

def play_song(song):
    pywhatkit.playonyt(song)

def system_control(command):
    if "shutdown" in command:
        speak("Shutting down the system.")
        os.system("shutdown /s /t 5")
    elif "restart" in command:
        speak("Restarting the system.")
        os.system("shutdown /r /t 5")
    elif "lock" in command:
        speak("Locking the system.")
        os.system("rundll32.exe user32.dll,LockWorkStation")

def take_screenshot():
    image = pyautogui.screenshot()
    image.save("screenshot.png")
    speak("Screenshot taken and saved as screenshot.png")


if __name__ == "__main__":
    wishMe()
    while True:
    
    # if 1:
        query = takeCommand().lower()

        # Logic for executing tasks based on query
        if 'open youtube' in query:
            webbrowser.open("youtube.com")

        elif 'open google' in query:
            webbrowser.open("google.com")

        elif 'open helper' in query:
            webbrowser.open("blackbox.ai")

        elif 'open amazon' in query:
            webbrowser.open("amazon.com")

        elif 'open flipkart' in query:
            webbrowser.open("flipkart.com")

        elif 'open compiler' in query:
            webbrowser.open("programiz.com")

        elif 'open spotify' in query:
            webbrowser.open("spotify.com")
        
        elif "wikipedia" in query:
            wikipedia_search(query)
        
        elif "play" in query:
                song = query.replace("play", "")
                speak(f"Playing {song} on YouTube")
                play_song(song)

        elif "shutdown" in query or "restart" in query or "lock" in query:
                    system_control(query)

        elif "screenshot" in query:
                take_screenshot()