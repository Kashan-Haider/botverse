from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from rag.chromaSetup import dense

def file_handling(file_content: str) -> bool:
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text(file_content)
        if not chunks:
            print("No valid text chunks found in document")
            return False
        processed_chunks = [
            chunk.strip() for chunk in chunks if len(chunk.strip().split()) >= 3
        ]
        documents = [
            Document(page_content=chunk.strip(), metadata={})
            for chunk in chunks
            if len(chunk.strip().split()) >= 3
        ]
        if not documents:
            print("No valid processed chunks found")
            return False
        successful_chunks = []
        for i, doc in enumerate(documents, start=1):
            try:
                dense.add_documents([doc])  # Add to Chroma (or other vector store)
                successful_chunks.append(doc)
                print(f"Adding chunk {i}/{len(documents)}")
            except Exception as e:
                print(f"Error adding chunk {i}: {e}")

        if not successful_chunks:
            print("No chunks were successfully added to the index")
            return False
        print(
            f"Successfully upserted {len(successful_chunks)} out of {len(processed_chunks)} chunks"
        )
        return True
    except Exception as e:
        print(f"Error in file handling: {e}")
        return False
