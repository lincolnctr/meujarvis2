import streamlit as st
from groq import Groq
import os
import json
import uuid
import time

# Definição do sys_msg
sys_msg = st.empty()
def print_sys_msg(msg):
    sys_msg.markdown(f'<p style="color: #00d4ff; font-weight: 700;">{msg}</p>', unsafe_allow_html=True)
    sys_msg.markdown(''.join(['<br>'] * 2))
    sys_msg.write('')

# Configuração da página
st.set_page_config(page_title="J.A.R.V.I.S. OS", page_icon="🤖", layout="wide")

# Configuração do estilo da página
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=JetBrains+Mono:wght@300;400&display=swap');

    html, body, [class*="css"], .stMarkdown, p, div {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stApp { background-color: #0e1117; color: #e0e0e0; }

    .jarvis-header {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 42px;
        font-weight: 700;
        color: #00d4ff;
        letter-spacing: 5px;
        text-shadow: 0 0 15px #00d4ffaa;
        animation: glow 3s infinite alternate;
        margin-bottom: 5px;
    }

    .jarvis-active-border {
        border: 2px solid #ff8c00;
        border-radius: 12px;
        padding: 20px;
        background: rgba(22, 27, 34, 0.95);
        box-shadow: 0 0 25px rgba(255, 140, 0, 0.25);
        animation: pulse-orange 2s infinite;
        margin-top: 10px;
        line-height: 1.6;
    }

    @keyframes pulse-orange {
        0% { border-color: #4b1d00; }
        50% { border-color: #ff8c00; }
        100% { border-color: #ffcc33; }
    }

    @keyframes glow {
        from { text-shadow: 0 0 10px #00d4ff; }
        to { text-shadow: 0 0 25px #00d4ff; }
    }
    </style>

    <script>
    function scrollToBottom() {
        const mainContent = window.parent.document.querySelector(".main");
        if (mainContent) {
            mainContent.scrollTo({ top: mainContent.scrollHeight, behavior: 'smooth' });
        }
    }
    const observer = new MutationObserver(scrollToBottom);
    observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """, unsafe_allow_html=True)

# Utilizando o sys_msg
print_sys_msg('J.A.R.V.I.S. está online.')
