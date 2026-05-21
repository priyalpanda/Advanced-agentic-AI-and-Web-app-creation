import chromadb
from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex
)
from chromadb import PersistentClient
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from duckduckgo_search import DDGS
import streamlit as st

# Initialize
llm = None

Settings.llm = Ollama(model="llama3.2", request_timeout=360.0)
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en")
Settings.embed_model = embed_model

# Define functions
def multiply(a: int, b: int) -> int:
    """Multiply two integers and return the result integer."""
    return a * b

def add(a: int, b: int) -> int:
    """Add two integers and return the result integer."""
    return a + b

def subtract(a: int, b: int) -> int:
    """Subtract second integer from the first and return the result integer."""
    return a - b

def search(query: str) -> str:
    """
    Args:
        query: user prompt

    Returns:
        context (str): search results to the user query
    """
    req = DDGS()
    response = req.text(query, max_results=3)
    context = ""
    for result in response:
        context += result['body']
    return context

# Define function tools
search_tool = FunctionTool.from_defaults(fn=search)
add_tool = FunctionTool.from_defaults(fn=add)
subtract_tool = FunctionTool.from_defaults(fn=subtract)
multiply_tool = FunctionTool.from_defaults(fn=multiply)

fntools = [multiply_tool, add_tool, subtract_tool, search_tool]

# Initialize agent
agent = ReActAgent.from_tools(fntools, llm=Settings.llm, max_iterations=15, verbose=True)

# Streamlit App
st.title("AI-Powered Q&A Agent")

user_query = st.text_input("Ask a question:", "")

if st.button("Submit"):
    if user_query:
        answer = agent.chat(user_query)
        st.write("Answer:", answer)
    else:
        st.warning("Please enter a question.")

