import streamlit as st
import openai
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
import ollama
import os

import os
from dotenv import load_dotenv
load_dotenv()

def get_setting(name,default=None):
    ## Read a setting from Streamlit secrets (used on Streamlit Cloud) or from .env / environment variables (used locally)
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name,default)

## Ollama server to connect to. Locally this is your own Ollama; when deployed it must be a server reachable from the internet
OLLAMA_HOST=get_setting("OLLAMA_HOST","http://localhost:11434")
OLLAMA_API_KEY=get_setting("OLLAMA_API_KEY")
ollama_headers={"Authorization":f"Bearer {OLLAMA_API_KEY}"} if OLLAMA_API_KEY else None
ollama_client=ollama.Client(host=OLLAMA_HOST,headers=ollama_headers)

## Langsmith Tracking (only enabled when an API key is provided in .env or Streamlit secrets)
langchain_api_key=get_setting("LANGCHAIN_API_KEY")
if langchain_api_key:
    os.environ["LANGCHAIN_API_KEY"]=langchain_api_key
    os.environ["LANGCHAIN_TRACING_V2"]="true"
    os.environ["LANGCHAIN_PROJECT"]="Simple Q&A Chatbot With Ollama"
else:
    os.environ["LANGCHAIN_TRACING_V2"]="false"

## Prompt Template
prompt=ChatPromptTemplate.from_messages(
    [
        ("system","You are a helpful assistant. Please respond to the user queries"),
        ("user","Question:{question}")
    ]
)

def generate_response(question,llm,temperature,max_tokens):
    ## keep_alive keeps the model loaded in memory between questions so it isn't reloaded each time
    llm=OllamaLLM(model=llm,temperature=temperature,num_predict=max_tokens,keep_alive="30m",
                base_url=OLLAMA_HOST,client_kwargs={"headers":ollama_headers} if ollama_headers else {})
    output_parser=StrOutputParser()
    chain=prompt|llm|output_parser
    ## Stream tokens as they are generated instead of waiting for the full answer
    return chain.stream({'question':question})

## #Title of the app
st.title("Enhanced Q&A Chatbot With Llama 3")


## Select the Ollama model (defaults to llama3)
## Only offer models that are actually available on the Ollama server
try:
    installed_models=[m.model for m in ollama_client.list().models]
except Exception:
    st.error(f"Could not connect to Ollama at `{OLLAMA_HOST}`. Running locally: make sure Ollama is installed and running (`ollama serve`). "
             "Deployed (e.g. Streamlit Cloud): set `OLLAMA_HOST` (and `OLLAMA_API_KEY` if needed) in the app's secrets to an Ollama server reachable from the internet. "
             "Then refresh this page.")
    st.stop()

if not installed_models:
    st.error("No Ollama models are installed. Pull one first, e.g. `ollama pull llama3`, then refresh this page.")
    st.stop()

default_model="llama3:latest"
default_index=installed_models.index(default_model) if default_model in installed_models else 0
llm=st.sidebar.selectbox("Select Open Source model",installed_models,index=default_index)

## Adjust response parameter
temperature=st.sidebar.slider("Temperature",min_value=0.0,max_value=1.0,value=0.7)
max_tokens = st.sidebar.slider("Max Tokens", min_value=50, max_value=300, value=150)

## MAin interface for user input
st.write("Go ahead and ask any question")
user_input=st.text_input("You:")

if user_input and user_input.strip():
    try:
        st.write_stream(generate_response(user_input.strip(),llm,temperature,max_tokens))
    except ollama.ResponseError as e:
        st.error(f"Ollama returned an error for model `{llm}`: {e.error}")
    except Exception as e:
        st.error(f"Something went wrong while generating the response: {e}")
else:
    st.write("Please provide the user input")


