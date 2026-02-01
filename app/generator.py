# app/generator.py

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

llm = None

def get_llm():
    """Get or create LLM instance lazily"""
    global llm
    if llm is None:
        llm = ChatOpenAI(model="gpt-4o")
    return llm


def generate_answer(question: str, context: str) -> str:
    llm = get_llm()
    prompt = f"""
Answer using ONLY the context below.

Context:
{context}

Question:
{question}
"""
    res = llm.invoke([
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=prompt)
    ])
    return res.content
