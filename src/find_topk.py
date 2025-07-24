import pandas as pd

def find_topk(model, query, top_k=3):
    """
    Find the top k results based on the query using the provided model.
    
    :param model: The model to use for finding results.
    :param query: The query string to search for.
    :param top_k: The number of top results to return.
    :return: A DataFrame containing the top k results.
    """
    
    retrieved_docs = model.invoke(query, top_k=top_k)
    print(f"Retrieved {len(retrieved_docs)} documents.")
    if len(retrieved_docs) < top_k:
        top_k = len(retrieved_docs)
    retrieved_docs_list = []

    # enumerate 파라미터 순서 수정: enumerate(iterable, start=1)
    for idx, doc in enumerate(retrieved_docs, 1):
        print(f"Result {idx}:")
        print(f"Index: {doc.metadata.get('index', 'Unknown')}")
        print(doc.page_content)
        print("="*200)

        retrieved_docs_list.append({
            "index": doc.metadata.get("index"),
            "text": doc.page_content,  # .get("text") 제거
        })
    
  
    return retrieved_docs_list[:top_k]  # top_k 개수만큼 반환