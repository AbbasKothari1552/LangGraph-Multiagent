import os
import sys
from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model


from app.core.config import QWEN_LLM, OPENAI_GPT_120


# Add credentials to environment variables
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Initialize LLM Model
llm = init_chat_model(OPENAI_GPT_120, temperature=0, model_provider='groq')

class LLMManager:
    _instance = None

    @staticmethod
    def get_llm():
        """Singleton LLM instance"""
        if LLMManager._instance is None:
            print("🔹 Initializing LLM...")
            LLMManager._instance = init_chat_model(
                model = OPENAI_GPT_120,
                temperature = 0,
                model_provider = 'groq'
            )

        return LLMManager._instance

llm = LLMManager.get_llm()  # Singleton for imports
