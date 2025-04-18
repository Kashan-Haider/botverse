from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import PineconeHybridSearchRetriever
from pinecone_text.sparse import BM25Encoder
from rag.pineconeSetup import connectPinecone

def get_retriever(index_name: str, alpha: float, bm25_model: BM25Encoder) -> PineconeHybridSearchRetriever:
    index = connectPinecone(index_name=index_name)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    retriever = PineconeHybridSearchRetriever(
        embeddings=embeddings,
        sparse_encoder=bm25_model,
        index=index,
        alpha=alpha,
        top_k=10,
        text_key="text",
    )
    return retriever

def file_handling(file_content: str) -> bool:
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text(file_content)
        if not chunks:
            print("No valid text chunks found in document")
            return False
        processed_chunks = [chunk.strip() for chunk in chunks if len(chunk.strip().split()) >= 3]
        if not processed_chunks:
            print("No valid processed chunks found")
            return False
        bm25_model = BM25Encoder()
        bm25_model.fit(processed_chunks)
        print("BM25 model fitted successfully")
        retriever = get_retriever("botverse", 0.7, bm25_model)
        successful_chunks = []
        for i, chunk in enumerate(processed_chunks, start=1):
            try:
                sparse_vector = bm25_model.encode_documents([chunk])
                if not sparse_vector[0]["indices"]:
                    print(f"Skipping chunk {i} - empty sparse vector")
                    continue
                print(f"Adding chunk {i}/{len(processed_chunks)}")
                retriever.add_texts([chunk])
                successful_chunks.append(chunk)
            except Exception as e:
                print(f"Error adding chunk {i}: {e}")
        if not successful_chunks:
            print("No chunks were successfully added to the index")
            return False
        print(f"Successfully upserted {len(successful_chunks)} out of {len(processed_chunks)} chunks")
        return True
    except Exception as e:
        print(f"Error in file handling: {e}")
        return False
