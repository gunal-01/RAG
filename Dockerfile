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

# Install Ollama
RUN curl -L https://ollama.com/download/linux/ollama.tar.gz -o ollama.tar.gz && \
    tar -xzf ollama.tar.gz -C /usr/local/bin && \
    rm ollama.tar.gz

# Copy the current directory contents into the container at /app
COPY . /app

# Install the dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the app will run on
EXPOSE 8501

# Run Ollama and the Streamlit app
CMD ["sh", "-c", "ollama serve & sleep 10 && streamlit run rag-app.py --server.port 8501"]