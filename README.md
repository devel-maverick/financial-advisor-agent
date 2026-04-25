

# DalalAI: Autonomous Financial Advisor Agent

DalalAI is an AI-powered financial advisor that goes beyond data reporting. It implements a **Reasoning & Causality Layer** to link Macro News → Sector Trends → Stock Performance → Portfolio Impact.

---

## Key Features

- **Causal Reasoning**: Automatically links external events (like RBI policy) to your portfolio movement.
- **Risk Detection**: Identifies concentration risks (e.g., >40% exposure in one sector).
- **Market Intelligence**: Real-time analysis of NIFTY 50, SENSEX, and FII/DII flows.
- **Self-Evaluation**: The agent "grades" its own reasoning quality and provides a confidence score.
- **Decoupled Architecture**: High-performance FastAPI backend with a premium Streamlit frontend.

---

## Tech Stack

- **LLM**: Groq (Llama 3)
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Observability**: Langfuse (Tracing & Logging)
- **Data**: Mock Market & Portfolio Datasets

---

## ⚙️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/devel-maverick/financial-advisor-agent.git
   cd financial-advisor-agent
   ```

2. **Set up Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file and add your keys:
   ```env
   GROQ_API_KEY=your_key_here
   LANGFUSE_PUBLIC_KEY=your_key_here
   LANGFUSE_SECRET_KEY=your_key_here
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```

---

## How to Run

### 1. Run via CLI (Quick Test)
To see the reasoning engine in the terminal:
```bash
python3 main.py
```

### 2. Run as a Full Web App (Recommended)
You need to run two services:

**Terminal 1 (Backend API)**:
```bash
python3 server.py
```

**Terminal 2 (Frontend Dashboard)**:
```bash
streamlit run app.py
```

---

## Screenshots

### Dashboard Overview

<img width="1511" height="800" alt="Screenshot 2026-04-25 at 4 23 08 PM" src="https://github.com/user-attachments/assets/ec3a48ec-8cae-4a4a-93de-0d601be87e25" />

### AI Reasoning & Causal Chain
<img width="1320" height="338" alt="Screenshot 2026-04-25 at 4 23 26 PM" src="https://github.com/user-attachments/assets/1c48dfe7-f418-4ed2-b775-3215720f53cd" />


---

## 🏗️ Architecture Overview
The system is divided into modular services:
- `DataLoader`: Handles JSON data ingestion.
- `PortfolioAnalytics`: Computes P&L and risk metrics.
- `MarketIntelligence`: Extracts news sentiment and sector trends.
- `Agent`: The core LLM reasoning engine.
- `Evaluator`: Self-evaluation layer for reasoning quality.
