from langchain.retrievers.ensemble import EnsembleRetriever
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Dense retriever
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
dense = Chroma(
    collection_name="example_collection",
    embedding_function=embedding,
    persist_directory="./chroma_langchain_db",  # Where to save data locally, remove if not necessary
)

# Sparse retriever (BM25)
texts = ["your_docs", "my docs"]
documents = [Document(page_content=text) for text in texts]
sparse = BM25Retriever.from_documents(documents)

# Combine both
retriever = EnsembleRetriever(
    retrievers=[dense.as_retriever(), sparse], weights=[0.5, 0.5]
)


query = "Your search query here"
results = retriever.invoke(query)
print(results)
