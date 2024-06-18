FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git

WORKDIR /app
COPY . ./

RUN pip3 install -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]