# AI-Infused-DevOps-Engine

## Contributor
- Shubhi Dubey
# AIDE – AI-Infused DevOps Engine

AIDE (AI-Infused DevOps Engine) is an intelligent self-healing CI/CD system designed to automate the detection, diagnosis, and resolution of DevOps pipeline failures using Generative AI and Agentic AI.

The system analyzes CI/CD error logs, identifies root causes, suggests fixes, and can automatically execute solutions with validation and rollback mechanisms.

---

## Features

- AI-based error diagnosis
- Root cause analysis
- Automated fix generation
- Confidence-based decision engine
- Self-healing CI/CD pipelines
- Validation and rollback support
- SQLite memory system for storing past fixes
- GitHub Actions integration
- Interactive Streamlit dashboard

---

##  Technologies Used

- Python
- Streamlit
- SQLite
- Groq API
- Llama 3.3 70B
- GitHub Actions
- LangChain
- DevOps Automation

---

##  Project Structure


AI-Infused-DevOps-Engine
│
├── layers/
│   ├── layer1_genai.py
│   ├── layer2_agent.py
│   └── layer3_executor.py
│
├── memory/
│   └── db.py
│
├── pages/
│   └── dashboard.py
│
├── utils/
│   └── prompts.py
│
├── app.py
├── requirements.txt
└── README.md