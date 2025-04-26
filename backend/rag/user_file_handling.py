from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.chromaSetup import getCollection


def file_handling(file_content: str, collection_name:str) -> bool:
    collection = getCollection(collection_name)
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )
        chunks = text_splitter.split_text(file_content)
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
        return True

    except Exception as e:
        print(f"Error in file handling: {e}")
        return False