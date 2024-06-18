# llm-gemini-rag-infobot-gke
This repository is based on my previous project [llm-gemini-rag-infobot](https://github.com/jameslinlaa/llm-gemini-rag-infobot)\
Deploy the app on the GKE, and host an open LLM model as the embedding or inference server. \
The short version of description for this web application is a RAG-based infobot to answer questions about Pokemon Go activity information.\
The details please refer to [llm-gemini-rag-infobot](https://github.com/jameslinlaa/llm-gemini-rag-infobot)

<br>
<br>
<br>

# Architecture on GKE
![Alt Text](https://github.com/jameslinlaa/llm-gemini-rag-infobot-gke/blob/main/static/architecture-on-gke.png)

More details in GKE official web site is in [doc](https://cloud.google.com/architecture/rag-capable-gen-ai-app-using-gke)

<br>
<br>
<br>

# Major changes and issues when deploying llm-gemini-rag-infobot-gke on GKE
1. Containerized streamlit app (including the frontend and backend)
2. langChain package version issue (solution: fixed version in requirements)
3. Move environment variables to stored in GCP secret manager
4. (Demo purpose) change online gemini api to open LLM model hosted by ollama 
5. (Demo purpose) change pinecorne to MongoDB Atlas

<br>
<br>
<br>

# Variables for MongoDB Atlas

MongoClient need a variable mongo_uri (including the access token) to access your vector database.\ 
Decided to move the variable mongo_uri into GCP secret manager because of app containerized. \
Just followed the GCP official document to access the latest version of secret (refer to the backend.app)\

Ref: [Connect to MongoDB Atlas](https://www.mongodb.com/docs/drivers/pymongo/#connect-to-mongodb-atlas)

<br>
<br>
<br>

# Deploy the app to Cloud Run
`NOTE: Need to change the code to access the online Gemini API instead of ollama before deploying to Cloud Run`

```
docker run -p 8501:8501 gcr.io/PROJECT_ID/gke-streamlit:latest

gcloud run deploy streamlit --source .
```

<br>
<br>
<br>

# Deploy the app to GKE
```
# Cloud Submit
gcloud builds submit --tag asia-east1-docker.pkg.dev/PROJECT_ID/mongodb/streamlit .



# Create AutoPilot cluster
gcloud container clusters create-auto pokemon  \   
--region=asia-east1  \
--project=PROJECT_ID \
--network=shared-vpc \
  --subnetwork=shared-subnet1 

# deploy deployment
kubectl apply -f deployment.yaml

# deploy service
kubectl apply -f service.yaml
```

<br>
<br>
<br>

# Resolve the no permission issue to access GCP secret manager from GKE

Ref: [Access secrets stored outside GKE clusters using client libraries](https://cloud.google.com/kubernetes-engine/docs/tutorials/workload-identity-secrets)

```
# Create k8s service account
kubectl create serviceaccount readonly-sa

# Grant secret manager permission 
gcloud secrets add-iam-policy-binding mongo_uri \
--member=principal://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/PROJECT_ID.svc.id.goog/subject/ns/default/sa/readonly-sa \
    --role='roles/secretmanager.secretAccessor' \
    --condition=None

```
<br>
<br>
<br>

# Resolve the no permission issue to access embedding API from GKE workload identity

Ref: [Authenticate to Google Cloud APIs from GKE workloads](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity#authenticating_to)

```
gcloud projects add-iam-policy-binding projects/PROJECT_ID \
    --role=roles/aiplatform.user \
--member=principal://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/PROJECT_ID.svc.id.goog/subject/ns/default/sa/readonly-sa \
    --condition=None


gcloud projects add-iam-policy-binding projects/PROJECT_ID \
    --role=roles/aiplatform.admin \ --member=principal://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/PROJECT_ID.svc.id.goog/subject/ns/default/sa/readonly-sa \
    --condition=None
```
<br>
<br>
<br>

# How to host open LLM model by ollama
Reference
- https://ollama.com/blog/embedding-models
- https://python.langchain.com/v0.2/docs/integrations/text_embedding/ollama/

Please refer to the yaml of ollama-cpu-deploy.yaml (eventually I still used L4 GPU)

<br>
<br>
<br>

# Ingest the Pokemon Go activity information into the vector store (MongoDB Atlas) 

I ran the code locally from my laptop, so the variable mongo_uri still in os environment (see ingestion.py)
I didn't containeried this part, and put it into the GKE yet. (only for demo purpose) 

```sh
python3 ingestion.py 
```

<br>
<br>
<br>

# Demo cases
Able to refer to [llm-gemini-rag-infobot](https://github.com/jameslinlaa/llm-gemini-rag-infobot)
