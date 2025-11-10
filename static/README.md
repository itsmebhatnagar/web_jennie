"# web_jennie_html" 
# Jennie AI Voice Assistant (Frontend)

Jennie is an interactive **AI voice assistant website** built using **HTML, CSS, and JavaScript**, connected to a Flask backend.  
It listens to your voice commands, responds using speech synthesis, and performs actions like opening websites or fetching Wikipedia summaries.

---

## 🌟 Features

- 🎙️ **Speech Recognition** (voice input)
- 🔊 **Speech Output** using `speechSynthesis`
- 🌐 Connects to backend via API (`/api/wish` & `/api/command`)
- 📚 Fetches info from **Wikipedia**
- 💡 **Command list modal** with available actions
- 💻 Modern **glassmorphism UI** design
- ⚡ Responsive for both desktop and mobile devices

---

## 🧠 Commands Jennie Understands

| Command | Action |
|----------|---------|
| "Open YouTube" | Opens YouTube |
| "Open Google" | Opens Google |
| "Open Flipkart" | Opens Flipkart |
| "Open Amazon" | Opens Amazon |
| "Open ChatGPT" | Opens ChatGPT |
| "Open Spotify" | Opens Spotify |
| "Search on Wikipedia (topic)" | Opens Wikipedia for (topic) |
| "My name is [Your Name]" | Saves your name |
| "What is my name" | Recalls saved name |

---

## 🛠️ Setup Instructions

### 1️⃣ Connect Backend

Replace the following line in your code with your actual backend URL:
```javascript
const BACKEND_URL = "https://jennie-backend.onrender.com";
