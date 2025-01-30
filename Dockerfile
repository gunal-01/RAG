# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install build tools and dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libsqlite3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama using official installation script
RUN curl https://ollama.ai/install.sh | sh

# Copy the current directory contents into the container at /app
COPY . /app

# Install the dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports for Streamlit and Ollama
EXPOSE 8502 11434

# Run Ollama and the Streamlit app
CMD ["sh", "-c", "\
    ollama serve & \
    sleep 5 && \
    ollama pull nomic-embed-text && \
    ollama pull mistral && \
    streamlit run rag-app.py --server.port 8502"]