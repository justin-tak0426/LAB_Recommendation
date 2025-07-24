from langchain_core.documents import Document
from langchain.retrievers import EnsembleRetriever
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_openai import AzureOpenAIEmbeddings

def load_retriever(docs: list[dict], k: int = 3):
    # Step 1: dict -> LangChain Document 변환
    langchain_docs = [
        Document(page_content=doc["text"], metadata={"index": doc["index"]})
        for doc in docs
    ]

    # Step 2: 임베딩 모델 로드
    embeddings = AzureOpenAIEmbeddings(model="text-embedding-3-small")

    # Step 3: 벡터 저장소 생성 (in-memory, not persisted)
    chroma_db = Chroma.from_documents(
        documents=langchain_docs,
        embedding=embeddings,
        collection_name="db_lab_info",
    )

    chroma_k_retriever = chroma_db.as_retriever(search_kwargs={"k": k})

    # Step 4: BM25 검색기 생성
    bm25_retriever = BM25Retriever.from_documents(langchain_docs)
    bm25_retriever.k = k  # 반환할 문서 수 설정

    # Step 5: 앙상블 검색기 생성
    emsemble_retrievers = [chroma_k_retriever, bm25_retriever]
    emsemble_retriever = EnsembleRetriever(
        retrievers=emsemble_retrievers,
        weights=[1, 0]
    )

    return emsemble_retriever
