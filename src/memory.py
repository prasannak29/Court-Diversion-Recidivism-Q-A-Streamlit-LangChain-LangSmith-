from langchain.memory import ConversationBufferMemory

def build_memory():
    # Stores prior human/AI turns; perfect for Q&A chat UIs
    return ConversationBufferMemory(memory_key="history", return_messages=True)
