
import streamlit as st
import asyncio
import sys

sys.path.append('/content/drive/MyDrive/cortex')
from mcp_client.client import ask_cortex

st.set_page_config(page_title="Cortex", layout="centered")

st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        max-width: 640px;
        padding-top: 4rem;
    }
    h1 {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #888;
        font-size: 0.9rem;
        margin-bottom: 2.5rem;
    }
    .stTextInput input {
        border-radius: 6px;
        border: 1px solid #ddd;
        padding: 10px 12px;
        font-size: 0.95rem;
    }
    .stButton button {
        border-radius: 6px;
        border: none;
        background-color: #111;
        color: white;
        padding: 8px 20px;
        font-size: 0.9rem;
    }
    .stButton button:hover {
        background-color: #333;
    }
    .answer-box {
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid #eee;
        line-height: 1.6;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>Cortex</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Search your coursework notes</div>", unsafe_allow_html=True)

question = st.text_input("", placeholder="Ask a question...", label_visibility="collapsed")
ask = st.button("Ask")

if ask and question:
    with st.spinner(""):
        answer = asyncio.run(ask_cortex(question))
    st.markdown(f"<div class='answer-box'>{answer}</div>", unsafe_allow_html=True)
