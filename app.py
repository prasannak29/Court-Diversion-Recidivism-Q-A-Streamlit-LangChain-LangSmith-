import os
import time
import uuid
from pathlib import Path

import streamlit as st
from langchain.memory import ChatMessageHistory

from src.config import REVIEWS_CHROMA_PATH
from src.memory import build_memory
from src.chains import build_chain, with_memory, run_with_metrics
from src.metrics import log_metrics, aggregate

st.set_page_config(page_title="Court Diversion Q&A", page_icon="⚖️", layout="wide")

st.title("⚖️ Court Diversion: Recidivism Q&A")
st.caption("Chat with your diversion dataset using retrieval-augmented generation. Memory, metrics, and LangSmith-ready.")

# Session setup
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "history_store" not in st.session_state:
    st.session_state.history_store = {}

# Sidebar
with st.sidebar:
    st.header("Settings")
    model = st.selectbox("Model", ["gpt-4-turbo-preview", "gpt-4o-mini", "gpt-4o"], index=0)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.0, 0.1)
    k = st.slider("Top-K (retriever)", 3, 20, 10, 1)
    st.divider()
    st.subheader("Metrics (local)")
    agg = aggregate()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Chats", agg["count"])
        st.metric("P95 Latency (s)", agg["p95_latency_s"])
    with col2:
        st.metric("Throughput (QPM, last 15m)", agg["throughput_qpm"])
        st.metric("Avg Cost (USD)", agg["avg_cost_usd"])
    st.caption("Detailed traces & spans appear in LangSmith when env vars are set.")

# Build chain + memory
base_chain = build_chain(model=model, temperature=temperature)
# LangChain Memory storage per session (RunnableWithMessageHistory expects a fetcher)
def get_session_history(session_id: str):
    if session_id not in st.session_state.history_store:
        st.session_state.history_store[session_id] = ChatMessageHistory()
    return st.session_state.history_store[session_id]

memory_chain = with_memory(base_chain, build_memory(), get_session_history)

# Chat UI
if "messages" not in st.session_state:
    st.session_state.messages = []

# show history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Ask about recidivism, IDs, timelines, etc...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            inputs = {"question": prompt}
            output, usage = run_with_metrics(
                memory_chain,
                inputs,
                config={"configurable": {"session_id": st.session_state.session_id}}
            )
            st.markdown(output)

            # Log metrics locally
            log_metrics({
                "ts": time.time(),
                "session_id": st.session_state.session_id,
                **usage
            })

    st.session_state.messages.append({"role": "assistant", "content": output})
