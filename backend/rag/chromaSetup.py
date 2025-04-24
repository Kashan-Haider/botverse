# import nltk
import chromadb
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# nltk.download("punkt")


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"}
)


class LangchainEmbeddingFunction:
    def __init__(self, embeddings):
        self.embeddings = embeddings

    def __call__(self, input):
        return np.array(self.embeddings.embed_documents(input))


chroma_client = chromadb.HttpClient(host="localhost", port=8001)

embedding_function = LangchainEmbeddingFunction(embeddings)
def getCollection(collection_name):
    collection = chroma_client.get_or_create_collection(
    name=collection_name, embedding_function=embedding_function
)
    return collection


def upsert_data(data):

    with open("../test-data.txt", "r") as file:
        content = file.read()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    chunks = text_splitter.split_text(content)
    print(f"Split text into {len(chunks)} chunks")

    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i : i + batch_size]
        batch_ids = [f"chunk_{i+j}" for j in range(len(batch_chunks))]

        try:
            collection.add(documents=batch_chunks, ids=batch_ids)
            print(
                f"✅ Added batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}"
            )
        except Exception as e:
            print(f"❌ Error adding batch {i//batch_size + 1}: {str(e)}")
            print(f"Error details: {e}")

    print("✅ Data processing complete!")

