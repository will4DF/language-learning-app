🌍 Zyra – Smart Language Learning App

Zyra is a web app built with Flask and Firebase that helps users learn English through adaptive, personalized lessons.
It analyzes what the user writes, determines their language level, and recommends fun learning content based on their interests.

---

🚀 Features

Adaptive English level detection (Beginner, Intermediate, Advanced)
Personalized suggestions based on hobbies
Firebase Authentication (Signup/Login)
Firestore database for saving user progress
Custom-designed responsive UI

---

🛠️ Tech Stack
| Layer | Tools Used |
|-------|-------------|
| Backend | Flask (Python) |
| Frontend | HTML, CSS |
| Database | Firebase Firestore |
| Auth | Firebase Authentication |
| NLP | spaCy, textstat |

---

⚙️ Quick Setup

```bash
# Clone repo
git clone https://github.com/will4DF/language-learning-app.git
cd language-learning-app

# Create and activate environment
python -m venv env
source env/bin/activate   # macOS/Linux
env\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

Then create a .env file with your Firebase Web API key:
FIREBASE_WEB_API_KEY=YOUR_FIREBASE_KEY_HERE
And add your Firebase service account key as firebase_key.json in the root folder.

▶️ Run the App
python app.py
