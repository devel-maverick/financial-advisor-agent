import os
from langfuse.openai import OpenAI
from services.logger import logger

class Agent:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY")
        )

    def analyze(self, user_prompt: str, system_prompt: str):
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