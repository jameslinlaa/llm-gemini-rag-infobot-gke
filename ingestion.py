import os

from langchain_google_vertexai import VertexAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_community.document_loaders import WebBaseLoader
# from langchain_pinecone import PineconeVectorStore

from pymongo import MongoClient
from langchain.vectorstores import MongoDBAtlasVectorSearch


MONGO_URI = os.environ["MONGO_URI"]
DB_NAME = "pokemon-2"
COLLECTION_NAME = "pokemon"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "vector_index"


EMBEDDING_FIELD_NAME = "embedding"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]

def ingest_docs() -> None:
    urls = [
            "https://pokemongolive.com/post/verdant-wonders-2024?hl=zh_Hant",
            "https://pokemongolive.com/post/weather-week-2024?hl=zh_Hant",
            "https://pokemongolive.com/post/kyogre-groudon-primal-raid-day-event?hl=zh_Hant",
    ]
    loader = WebBaseLoader(urls)

    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
        chunk_size=5000,
        chunk_overlap=150,
    )

    documents = text_splitter.split_documents(docs)

    print(f"Going to add {len(documents)} to altas")

    embeddings = VertexAIEmbeddings(model_name="textembedding-gecko@001")

    # index_name=os.getenv("PINECONE_INDEX_NAME")
    # print(index_name)

    # don't mix up multiple pages
    chunk_size = 1 
    for i in range(0, len(documents)):
        print(f"iteration {i}...")
        chunked_documents = documents[i:i+chunk_size]
        x = MongoDBAtlasVectorSearch.from_documents(
        documents=chunked_documents, embedding=embeddings, collection=MONGODB_COLLECTION, index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME
    )
    print("****Loading to vectorestore done ***")




if __name__ == "__main__":
    ingest_docs()
