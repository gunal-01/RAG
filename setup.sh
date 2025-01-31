#!/bin/bash
pip install -r requirements.txt
streamlit run rag-app.py --server.port $PORT