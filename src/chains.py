from typing import Dict, Any
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
)
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.callbacks import get_openai_callback

from .vectorstore import get_reviews_retriever
from .pricing import estimate_cost
from langchain_core.runnables import RunnableLambda

REVIEW_TEMPLATE_STR = """You are a court data expert.
You have data about diversion data going back several years.
ID column is an identifier. The values in this column repeat several times as same instance of an individual might repeat because the person might have come back into the system because of recidivism.
The dates shown in OFFENSE DATE, RECEIVED DATE, DIVERSION PLACEMENT DATE and TERMINATION DATE column provide an idea when that person might have committed the offense again, a referral was received again and officially the person was put on diversion and then after being on the program was terminated.
We have a column RECIDIVISM with values YES or NO.
Recidivism criteria: consider only rows with non-null TERMINATION DATE. For the same ID, if a later RECEIVED DATE occurs after a prior TERMINATION DATE, that indicates recidivism.
Answer questions using the retrieved context. If unsure, say so.


{context}
"""

def build_chain(model: str = "gpt-4-turbo-preview", temperature: float = 0.0):
    review_system_prompt = SystemMessagePromptTemplate(
        prompt=PromptTemplate(input_variables=["context"], template=REVIEW_TEMPLATE_STR)
    )
    review_human_prompt = HumanMessagePromptTemplate(
        prompt=PromptTemplate(input_variables=["question"], template="{question}")
    )
    messages = [review_system_prompt, review_human_prompt]
    review_prompt_template = ChatPromptTemplate(input_variables=["context", "question"], messages=messages)

    chat_model = ChatOpenAI(model=model, temperature=temperature)
    output_parser = StrOutputParser()

    raw_retriever = get_reviews_retriever(k=10)
    retriever = RunnableLambda(lambda x: raw_retriever.invoke(x["question"]))

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | review_prompt_template
        | chat_model
        | output_parser
    )
    return chain

def with_memory(chain, memory, get_session_history):
    """Wrap the base chain with message history using RunnableWithMessageHistory."""
    return RunnableWithMessageHistory(
        chain,
        get_session_history=get_session_history,
        input_messages_key="question",
        history_messages_key="history",
    )

def run_with_metrics(runnable, inputs: Dict[str, Any], config: Dict[str, Any] | None = None):
    """Execute chain while collecting token usage and simple latency metrics."""
    from time import perf_counter
    start = perf_counter()
    with get_openai_callback() as cb:
        output = runnable.invoke(inputs, config=config or {})
        latency = perf_counter() - start

        usage = {
            "prompt_tokens": cb.prompt_tokens,
            "completion_tokens": cb.completion_tokens,
            "total_tokens": cb.total_tokens,
            "cost_est_usd": cb.total_cost if hasattr(cb, "total_cost") and cb.total_cost else estimate_cost(cb.prompt_tokens, cb.completion_tokens),
            "latency_seconds": latency,
        }
    return output, usage
