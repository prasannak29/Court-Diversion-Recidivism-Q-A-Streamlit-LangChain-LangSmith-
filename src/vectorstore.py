from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from .config import REVIEWS_CHROMA_PATH

def get_reviews_retriever(k: int = 10):
    vs = Chroma(
        persist_directory=REVIEWS_CHROMA_PATH,
        embedding_function=OpenAIEmbeddings(),
    )
    return vs.as_retriever(k=k)
