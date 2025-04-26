import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"}
)

class LangchainEmbeddingFunction:
    def __init__(self, embeddings):
        self.embeddings = embeddings

    def __call__(self, input):
        return np.array(self.embeddings.embed_documents(input))


chroma_client = chromadb.PersistentClient(path="./chrromadb-local-data")

embedding_function = LangchainEmbeddingFunction(embeddings)


def getCollection(collection_name):
    collection = chroma_client.get_or_create_collection(
        name=collection_name, embedding_function=embedding_function
    )
    return collection
