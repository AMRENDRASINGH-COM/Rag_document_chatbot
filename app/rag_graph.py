# app/rag_graph.py

from app.retriever import retrieve
from app.generator import generate_answer


def compute_confidence(sim_scores: list[float]) -> float:
    if not sim_scores:
        return 0.0

    avg_score = sum(sim_scores) / len(sim_scores)

    # cosine similarity is already between [-1, 1], mostly [0,1] for embeddings
    confidence = max(0.0, min(1.0, avg_score))
    return round(confidence, 2)


def rag(question, documents, doc_embeddings, k=2):
    retrieved_docs, sim_scores = retrieve(question, documents, doc_embeddings, k=k)

    context = "\n".join(retrieved_docs)
    answer = generate_answer(question, context)

    confidence = compute_confidence(sim_scores)

    return answer, retrieved_docs, confidence
