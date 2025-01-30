# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Combine RUN commands to reduce layers
RUN apt-get update && apt-get install -y \
    gcc \
    libsqlite3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl https://ollama.ai/install.sh | sh

# Copy only necessary files first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy remaining files
COPY . .

# Expose ports for Streamlit and Ollama
EXPOSE 8502 11434

# Run Ollama and the Streamlit app
CMD ["sh", "-c", "ollama serve & sleep 5 && ollama pull nomic-embed-text && ollama pull mistral && streamlit run rag-app.py --server.port 8502"]