from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv(override=True)

class FinancialAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def analyze(self, user_prompt: str,system_prompt:str):
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt}
                ,
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content

