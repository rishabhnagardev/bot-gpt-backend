def retrieve_relevant_chunks(documents, query, top_k=2):
    chunks = []
    query_lower = query.lower()

    for doc in documents:
        if query_lower in doc.content.lower():
            chunks.append(doc.content)

    return chunks[:top_k]
