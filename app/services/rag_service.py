def retrieve_relevant_chunks(documents, query, top_k=2):
    """Return up to `top_k` document chunks relevant to `query`.

    Heuristic behaviours:
    - If the query is a generic summarization request (contains "summar"),
      return the full document content so the LLM can summarise it.
    - Otherwise perform a simple substring match to find relevant docs.
    """
    chunks = []
    query_lower = (query or "").lower()

    # If user asked to summarize or provided a very short/generic query,
    # include full documents so the LLM has material to work with.
    if "summar" in query_lower or len(query_lower.split()) < 4:
        for doc in documents:
            chunks.append(doc.content)
        return chunks[:top_k]

    # Fallback simple relevance by substring match
    for doc in documents:
        if query_lower in (doc.content or "").lower():
            chunks.append(doc.content)

    return chunks[:top_k]
