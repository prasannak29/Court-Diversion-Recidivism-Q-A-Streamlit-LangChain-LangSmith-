import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
# LangSmith auto-inits from env vars:
#   LANGCHAIN_TRACING_V2=true
#   LANGCHAIN_API_KEY=ls-...
#   LANGCHAIN_PROJECT=your-project-name

REVIEWS_CHROMA_PATH = os.getenv("REVIEWS_CHROMA_PATH", "chroma_data/ALM")

# Pricing for cost estimates ($ per 1k tokens)
PRICE_INPUT_PER_1K = float(os.getenv("PRICE_INPUT_PER_1K", "0.01"))
PRICE_OUTPUT_PER_1K = float(os.getenv("PRICE_OUTPUT_PER_1K", "0.03"))
