# Jennie AI Voice Assistant (Backend)

Jennie is a simple AI-powered voice assistant backend built with **Flask**.  
It responds to user voice/text commands such as opening websites, greeting the user, and answering simple Wikipedia queries.  
The backend can be connected to a frontend to create an interactive web-based AI assistant.

---

## 🚀 Features

- Greets user based on the time of day (morning, afternoon, evening)
- Responds to common commands:
  - Open YouTube, Google, Flipkart, Amazon, Spotify, ChatGPT (Helper)
- Wikipedia integration for quick summaries
- Remembers user's name using a local `memory.json` file
- Simple REST API with JSON responses
- CORS enabled for frontend connection

---

## 🧠 Example Commands

| Command | Response |
|----------|-----------|
| "Open YouTube" | "Opening YouTube..." |
| "Open Google" | "Opening Google..." |
| "Who is Elon Musk Wikipedia" | "According to Wikipedia: Elon Musk is..." |
| "My name is Harshil" | "Nice to meet you, Harshil!" |
| "What is my name" | "Harshil" |

---

## 🛠️ Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/jennie-ai-backend.git
   cd jennie-ai-backend
2. **Install Dependices**
   pip install -r requirements.txt

3. **Run The Server**
   python FirstProgram.py
