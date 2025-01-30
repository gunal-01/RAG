# RAG (Retrieval Augmented Generation) Application

## Overview
A local RAG (Retrieval Augmented Generation) application built with Streamlit and Ollama. The application processes JSON data from APIs, stores it in a vector database (ChromaDB), and uses Mistral AI for generating responses to user queries.

## Features
- JSON data processing and flattening
- Vector storage with ChromaDB
- AI-powered responses using Mistral
- User-friendly Streamlit interface
- Docker support for containerized deployment

## Requirements
- Windows 10/11
- Python 3.11+
- Docker Desktop (optional)
- Git
- VS Code (recommended)

## Installation

### Local Development Setup
```powershell
# Clone repository
git clone <repository-url>
cd RAG

# Create virtual environment
python -m venv myenv

# Activate virtual environment
.\myenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Ollama
# Download from https://ollama.com/download
# Run installer and start service

# Pull required models
ollama pull nomic-embed-text
ollama pull mistral

# Start application
streamlit run rag-app.py --server.port 8502
