# Appointment Chatbot
![Python](https://img.shields.io/badge/Python-3670A0?style=flat&logo=python&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=langchain) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white) ![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=flat&logo=googlecloud&logoColor=white)

An intelligent chatbot that interacts with users to schedule appointments using Streamlit, LangChain, and Google Calendar API.

## 🔧 Installation

Clone the repository
```shell
git clone https://github.com/Oscaro92/appointment-agent.git
cd appointment-agent
```
Create a virtual environment
```shell
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```
Install dependencies
```shell
pip install -r requirements.txt
```

## ⚙️ Configuration

### Google Calendar API

1. Create a project in the [Google Cloud Console](https://console.cloud.google.com)
2. Enable the Google Calendar API
3. Create OAuth 2.0 credentials
4. Copy the `credentials.json` file to the project folder
5. Create a `.env` file with the following variables:
```
GMAIL_USER=you@gmail.com
OPENAI_API_KEY=sk-...
```

## 🚀 Usage

# Run the Streamlit app
```shell
streamlit run chat.py
```

## 📁 Project Structure

```
appointment-agent/
├── agent.py            # Agent
├── chat.py             # Chatbot with streamlit
├── function.py         # Google Calendar integration
├── requirements.txt    # Dependencies
├── .env                # Environment variables
└── README.md           # Documentation
```

## 📝 License

This project is licensed under the MIT License.
