import streamlit as st
import requests
from langchain.text_splitter import CharacterTextSplitter
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os
import shutil
import time

# Initialize session state
if 'json_data' not in st.session_state:
    st.session_state.json_data = None
if 'text_chunks' not in st.session_state:
    st.session_state.text_chunks = None
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None

# 1. Fetch JSON data from an endpoint with timeout
def fetch_json(endpoint_url, timeout=10):
    """Fetch JSON data from a given API endpoint."""
    if not endpoint_url.startswith("http"):
        return {"error": "Invalid URL. Please enter a valid URL starting with http or https."}
    try:
        response = requests.get(endpoint_url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# 2. Convert JSON data to a flattened text format
def parse_json_to_text(json_data):
    """Convert nested JSON into a plain text representation."""
    def flatten(obj, parent_key='', sep='.'):
        """Flatten nested JSON recursively."""
        items = []
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    items.extend(flatten(item, f"{new_key}[{i}]", sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    flattened = flatten(json_data)
    return "\n".join(f"{k}: {v}" for k, v in flattened.items())

# 3. Text splitting
def split_text(text):
    """Split text into smaller chunks."""
    text_splitter = CharacterTextSplitter(chunk_size=7500, chunk_overlap=100)
    return text_splitter.split_text(text)

# 4. Retry mechanism to delete directory
def safe_rmtree(directory, retries=5, delay=1):
    """Safely remove a directory with retry mechanism."""
    for attempt in range(retries):
        try:
            shutil.rmtree(directory)
            return True
        except PermissionError as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise e
    return False

# 5. Fetch and process data
def fetch_and_process_data(endpoint_url):
    json_data = fetch_json(endpoint_url)
    if "error" in json_data:
        st.error(f"Error fetching JSON data: {json_data['error']}")
        return
    text_data = parse_json_to_text(json_data)
    text_chunks = split_text(text_data)
    embedding_model = OllamaEmbeddings(model="nomic-embed-text")
    persist_directory = "./chroma_db"
    if os.path.exists(persist_directory):
        safe_rmtree(persist_directory)
    vectorstore = Chroma.from_texts(
        texts=text_chunks,
        collection_name="rag-chroma",
        embedding=embedding_model,
        persist_directory=persist_directory
    )
    vectorstore.persist()
    st.session_state.json_data = json_data
    st.session_state.text_chunks = text_chunks
    st.session_state.vectorstore = vectorstore
    st.success("Data fetched and processed successfully.")

# 6. Answer query
def answer_query(question):
    if not st.session_state.vectorstore:
        st.error("Please fetch data before asking a query.")
        return
    retriever = st.session_state.vectorstore.as_retriever()
    model_local = ChatOllama(model="mistral")
    after_rag_template = """Answer the question based only on the following context:
{context}
Question: {question}
"""
    after_rag_prompt = ChatPromptTemplate.from_template(after_rag_template)
    after_rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | after_rag_prompt
        | model_local
        | StrOutputParser()
    )
    try:
        result = after_rag_chain.invoke(question)
        return str(result)
    except Exception as chain_error:
        st.error(f"An error occurred during chain invocation: {chain_error}")
        return None

# Streamlit UI
st.title("Backend data Query with Mistral")
st.write("Enter a EndPoint URL to fetch data and then ask a question to query")

# Input fields
endpoint_url = st.text_input("Enter the Backend EndPoint URL:")
question = st.text_input("Enter the Question:")

# Fetch data button
if st.button("Fetch Data"):
    fetch_and_process_data(endpoint_url)

# Ask query button
if st.button("Ask Query"):
    result = answer_query(question)
    if result:
        st.success("Result:")
        st.text(result)
