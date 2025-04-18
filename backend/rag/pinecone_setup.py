from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from dotenv import load_dotenv
import os

def connect_pinecone(index_name: str) -> Pinecone.Index:
    load_dotenv()
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

    pc = Pinecone(api_key=PINECONE_API_KEY)
    if index_name not in [index.name for index in pc.list_indexes()]:
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="dotproduct",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

    index = pc.Index(index_name)
    return index


connect_pinecone('test-index')
