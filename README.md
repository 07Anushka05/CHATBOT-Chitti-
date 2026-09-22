<div align="center">

# 🤖 Chitti

### Your Personal AI Assistant — Private, Local, and Beautifully Simple

*A premium, glassmorphic AI chatbot built with Streamlit, powered by local LLMs via Ollama.*

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-000000?style=flat&logo=ollama&logoColor=white)](https://ollama.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## ✨ Overview

**Chitti** is a full-featured, self-hosted AI chatbot with a polished, animated interface. Unlike typical cloud chatbots, Chitti runs on **local LLMs through Ollama**, giving you full control over your data and conversations — with user accounts, persistent chat history, and a UI that doesn't feel like a weekend project.

> 💡 Named after the beloved robot from *Enthiran*, Chitti aims to be a warm, intelligent companion — not just a query box.

---

## 🚀 Features

- 🔐 **User Authentication** — Secure register/login system with hashed passwords (SQLite-backed)
- 💬 **Persistent Chat History** — Every conversation is saved per-user and can be revisited, renamed, or deleted
- 🎙️ **Voice Input** — Talk to Chitti using built-in speech-to-text
- 📎 **File Analysis** — Upload PDFs, code files, docs, spreadsheets, and images directly into the conversation
- 🌗 **Dark / Light Mode** — Fully themed UI that adapts instantly
- ✨ **Live Animated Background** — Ambient floating gradient orbs for a premium feel (toggleable)
- 📤 **Export Conversations** — Download any chat as JSON or plain text
- 🧠 **Context-Aware Responses** — Maintains conversation flow without robotic, repetitive greetings
- ⚡ **Runs Fully Local** — No API keys, no cloud costs — powered by [Ollama](https://ollama.com/)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend / UI | [Streamlit](https://streamlit.io/) |
| LLM Runtime | [Ollama](https://ollama.com/) |
| Voice Input | `streamlit-mic-recorder` |
| Database | SQLite |
| File Parsing | `PyPDF2` |
| Language | Python 3.9+ |

---

## 📸 Preview

> *Add a screenshot or GIF of Chitti in action here — drag an image into this section on GitHub, e.g.:*
<img width="1886" height="915" alt="image" src="https://github.com/user-attachments/assets/940514ae-92f9-4c19-8d51-5d6b7c7338de" />
<img width="1911" height="911" alt="image" src="https://github.com/user-attachments/assets/612c76a7-10bd-45ed-bd96-c5005a4593a2" />
<img width="1917" height="861" alt="image" src="https://github.com/user-attachments/assets/75a0451d-0a47-478f-b454-8e8b0d6e6f91" />


---

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- [Ollama](https://ollama.com/download) installed and running locally
- A pulled model (e.g. `gemma3:4b`, the default used by Chitti):
  ```bash
  ollama pull gemma3:4b
  ```

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/chitti-ai-chatbot.git
cd chitti-ai-chatbot

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Make sure Ollama is running
ollama serve

# 5. Launch the app
streamlit run app2.py
```

The app will open automatically at `http://localhost:8501`.

---

## 📁 Project Structure

```
chitti-ai-chatbot/
├── app2.py            # Main Streamlit application (UI, auth, chat logic)
├── database.py        # SQLite database layer (users, sessions, messages)
├── main.py            # Lightweight CLI chatbot prototype (LangChain + Ollama)
├── requirements.txt   # Python dependencies
├── .gitignore         # Files/folders excluded from version control
└── README.md          # You are here
```

---

## ⚙️ Configuration

Chitti defaults to the `gemma3:4b` model. To use a different local model, pull it with Ollama and update the default in `app2.py`:

```python
if "model" not in st.session_state:
    st.session_state.model = "gemma3:4b"   # <- change this
```

---

## 🗺️ Roadmap

- [ ] Multi-model switcher in the UI (choose model per chat)
- [ ] Streaming responses token-by-token
- [ ] Shareable chat links
- [ ] Docker deployment support
- [ ] Multi-language support for voice input

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Made with ❤️ and a lot of ☕

</div>
