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





file_content = [
    "Toyota Fortuner Legender  2022 is for sale at I- 8, Islamabad Islamabad. The model of this car is 2022 with mileage of 5 km. The engine type is Diesel and the transmission is Automatic. It is Un-Registered and comes in White color. The car is Local with an engine capacity of 2800 cc. It is a SUV that includes features like ABS,AM/FM Radio,Air Bags,Air Conditioning,Alloy Rims,Cassette Player,Cruise Control,Immobilizer Key,Keyless Entry,Navigation System,Power Locks,Power Mirrors,Power Steering,Power Windows. More details can be found at https://www.pakwheels.com/used-cars/toyota-fortuner-2022-for-sale-in-islamabad-5980157. The price of this car is .",
    "Toyota Premio X EX Package 1.8 2018 is for sale at Askari 6, Peshawar KPK. The model of this car is 2018 with mileage of 17,000 km. The engine type is Petrol and the transmission is Automatic. It is Un-Registered and comes in Peral White color. The car is Imported with an engine capacity of 1800 cc. It is a Sedan that includes features like ABS,AM/FM Radio,Air Bags,Air Conditioning,Alloy Rims,Cruise Control,DVD Player,Immobilizer Key,Keyless Entry,Navigation System,Power Locks,Power Mirrors,Power Steering,Power Windows. More details can be found at https://www.pakwheels.com/used-cars/toyota-premio-2018-for-sale-in-peshawar-6084348. The price of this car is 8500000.0.",
    "Honda City Aspire 1.3 i-VTEC 2016 is for sale at I- 8, Islamabad Islamabad. The model of this car is 2016 with mileage of 59,000 km. The engine type is Petrol and the transmission is Manual. It is Islamabad and comes in White color. The car is Local with an engine capacity of 1300 cc. It is a Sedan that includes features like ABS,AM/FM Radio,Air Conditioning,Alloy Rims,CD Player,DVD Player,Immobilizer Key,Keyless Entry,Navigation System,Power Locks,Power Mirrors,Power Steering,Power Windows. More details can be found at https://www.pakwheels.com/used-cars/honda-city-2016-for-sale-in-islamabad-6142613. The price of this car is 2375000.0.",
    "Suzuki Bolan VX Euro II 2018 is for sale at Dhok Sayedan Road, Rawalpindi Punjab. The model of this car is 2018 with mileage of 55,000 km. The engine type is Petrol and the transmission is Manual. It is Islamabad and comes in White color. The car is Local with an engine capacity of 800 cc. It is a Van that includes features like AM/FM Radio,Immobilizer Key. More details can be found at https://www.pakwheels.com/used-cars/suzuki-bolan-2018-for-sale-in-rawalpindi-6150027. The price of this car is 1050000.0.",
   ]


file_handling(file_content, 'cars')