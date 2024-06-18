import os
from typing import Any, Dict, List

from langchain_google_vertexai import VertexAIEmbeddings
#from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA
from langchain_google_vertexai import ChatVertexAI
from langchain.chains import ConversationalRetrievalChain

from pymongo import MongoClient
from langchain_community.vectorstores import MongoDBAtlasVectorSearch

import langchain 
# langchain.debug = True

from google.cloud import secretmanager
from langchain_community.llms import Ollama



## 1. Access the mongo_uri from GCP secret manager
client = secretmanager.SecretManagerServiceClient()
project_id = "PROJECT_ID"
secret_id = "SECRET_ID"
version_id = "latest"

# Build the resource name of the secret version.
name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

# Access the secret version.
response = client.access_secret_version(request={"name": name})
payload = response.payload.data.decode("UTF-8")


## 2. set up Mongodb Atlas variable
MONGO_URI = payload
DB_NAME = "pokemon-2"
COLLECTION_NAME = "pokemon"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "vector_index"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]



def run_g_llm(query: str, chat_history: List[Dict[str, Any]] = []):
    embeddings = VertexAIEmbeddings(model_name="textembedding-gecko@001")  # Dimention 768

    ## [DEMO purpose] 
    ## vector store is Mongodb Atlas
    vector_search = MongoDBAtlasVectorSearch.from_connection_string(
        MONGO_URI,
        DB_NAME + "." + COLLECTION_NAME,
        embeddings,
        index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME
    )

    retriever = vector_search.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 200,
            "post_filter_pipeline": [{"$limit": 25}]
        }
    )
    # vectorstore = PineconeVectorStore(index_name=os.environ["PINECONE_INDEX_NAME"], embedding=embeddings)
    
    
    ## [DEMO purpose] 
    ## Replace online Gemini 1.5 pro API by hosting open LLM model on GKE 
    # chat = ChatVertexAI(
    #     # Reduce the possibility of the answer is truncated 
    #     max_output_tokens=2000
    # )
    llm = Ollama(
        base_url="http://ollama.default.svc.cluster.local:11434",
        model="yabi/breeze-7b-32k-instruct-v1_0_q8_0",
    )

    qa = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=retriever, return_source_documents=True
    )

    return qa({"question": query, "chat_history": chat_history})

