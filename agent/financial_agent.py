import os
from typing import List, Dict
from langfuse.openai import OpenAI
from services.logger import logger

CHAT_SYSTEM_PROMPT = """You are DalalAI, an expert Indian financial advisor chatbot.

You can answer ANY question related to:
- Finance, investing, stock markets (NSE/BSE)
- Mutual funds, SIPs, asset allocation
- Portfolio strategy, risk management
- Market trends, sector analysis
- Financial planning, taxation basics
- RBI policy, FII/DII flows, macro-economics

RULES:
1. If portfolio context is provided, use it to personalize your answers.
2. Always use specific numbers, percentages, and data when available.
3. Be concise but thorough. Use bullet points for clarity.
4. If asked about a specific stock/sector in the user's portfolio, reference their holdings.
5. If a question is outside finance, politely redirect.
6. Never give guaranteed return predictions — always mention risks.
7. For Indian markets, use INR (₹) and Indian conventions (Lakhs, Crores).
"""


class Agent:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY")
        )

    def analyze(self, user_prompt: str, system_prompt: str) -> str:
        logger.info("Sending prompt to LLM")
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        
        logger.info("Received response from LLM successfully.")
        return response.choices[0].message.content

    def chat(self, user_message: str, chat_history: List[Dict[str, str]], portfolio_context: str = "") -> str:
        logger.info(f"Chat request: {user_message[:80]}...")

        system = CHAT_SYSTEM_PROMPT
        if portfolio_context:
            system += f"\n\n--- ACTIVE PORTFOLIO CONTEXT ---\n{portfolio_context}\n--- END CONTEXT ---"

        messages = [{"role": "system", "content": system}]
        for msg in chat_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.4
        )

        reply = response.choices[0].message.content
        logger.info("Chat response received from LLM.")
        return reply