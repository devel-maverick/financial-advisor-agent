# DalalAI: Autonomous Financial Advisor Agent

DalalAI is an AI tool that helps you understand your portfolio's performance. Instead of just showing numbers, it explains the reasons behind your portfolio's movement by connecting market news to your specific stocks.

---

## The Problem
Most portfolio trackers only show you how much money you made or lost. They don't tell you "Why".
- Did your portfolio fall because of a change in government policy or just a bad day for your stocks?
- Is one sector taking up too much of your portfolio?
- Which news headline actually matters for the stocks you own?

DalalAI solves this by looking at news, sector trends, and stock prices to give you a clear explanation.

---

## Key Features

- **Reasoning Flow**: Automatically connects news (like RBI decisions) to your portfolio's movement.
- **Risk Alerts**: Finds if you have too much money in one sector (concentration risk) and identifies negative trends.
- **Market Context**: Shows how the overall market (NIFTY 50, SENSEX) and big investors (FII/DII) are behaving.
- **Self-Checking**: The AI checks its own work to make sure the analysis is accurate before showing it to you.
- **Clean Dashboard**: A simple web interface to see all your data and the AI's reasoning in one place.
- **Chat with DalalAI**: Ask any question about finance, markets, stocks, mutual funds, or your specific portfolio — the AI responds with context-aware answers.

---

## How it Works

The system follows a simple step-by-step process:

1.  **Get Data**: It collects your portfolio details, latest news, and market prices from files.
2.  **Analyze**: 
    - It calculates your P&L and checks for risks.
    - It reads the news to see if the sentiment is positive or negative.
3.  **Build Context**: It puts all this information together into a single summary for the AI.
4.  **Reasoning**: The AI (Llama 3) reads the summary and explains the "Why" behind the movements.
5.  **Evaluation**: Another part of the system scores the AI's answer to ensure it is logical and uses correct data.

---

## Project Structure

```bash
├── agent/
│   └── financial_agent.py   # The AI's brain (Groq/Llama 3)
├── services/
│   ├── data_loader.py       # Reads the data files
│   ├── portfolio_analytics.py # Calculates P&L and risks
│   ├── market_intelligence.py  # Analyzes news and market trends
│   ├── evaluator.py         # Checks if the AI's answer is good
│   ├── langfuse.py          # Monitors the AI's performance
│   └── logger.py            # Records what the system is doing
├── main.py                  # Entry point to run in terminal
├── server.py                # The backend server (API)
├── app.py                   # The web dashboard (Streamlit)
├── data/                    # Folder containing your data files
└── requirements.txt         # List of tools needed to run this
```

---

## Tech Stack

- **AI Model**: Llama 3.3 via Groq (for fast results).
- **Backend**: FastAPI (Python).
- **Frontend**: Streamlit (for the dashboard).
- **Monitoring**: Langfuse (to track AI responses).

---

## Installation and Setup

1. **Clone the project**:
   ```bash
   git clone https://github.com/devel-maverick/financial-advisor-agent.git
   cd financial-advisor-agent
   ```

2. **Create a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install required tools**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your API Keys**:
   Create a file named `.env` in the folder and add:
   ```env
   GROQ_API_KEY=your_key_here
   LANGFUSE_PUBLIC_KEY=your_key_here
   LANGFUSE_SECRET_KEY=your_key_here
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```

---

## How to Run

### 1. Run in Terminal
To see the analysis directly in your command line:
```bash
python3 main.py
```

### 2. Run the Web Dashboard
You need to open two terminals:

**Terminal 1 (Start the Backend)**:
```bash
python3 server.py
```

**Terminal 2 (Start the Dashboard)**:
```bash
streamlit run app.py
```

---

## Screenshots

### Dashboard Overview
<img width="1511" height="800" alt="Dashboard" src="https://github.com/user-attachments/assets/ec3a48ec-8cae-4a4a-93de-0d601be87e25" />

### AI Reasoning
<img width="1320" height="338" alt="Reasoning" src="https://github.com/user-attachments/assets/1c48dfe7-f418-4ed2-b775-3215720f53cd" />

---

## API Endpoints

| Path | Method | What it does |
| :--- | :--- | :--- |
| `/portfolio/{id}` | `GET` | Gets portfolio and market data. |
| `/analyze` | `POST` | Asks the AI to analyze the portfolio. |
| `/chat` | `POST` | Chat with DalalAI about finance or your portfolio. |
| `/health` | `GET` | Checks if the server is running. |

---

## Monitoring
We use **Langfuse** to keep track of every AI response. This helps us see how fast the AI is and if it is giving helpful answers.
