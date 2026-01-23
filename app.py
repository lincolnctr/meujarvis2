import streamlit as st
from groq import Groq
import os
import json
import uuid
import time

# ---------------------------------------------------------
# 1. DESIGN HUD (ESTILO STARK) - MANTIDO EM BLOCO ÚNICO
# ---------------------------------------------------------
st.set_page_config(page_title="J.A.R.V.I.S. OS", page_icon="🤖", layout="wide")
st.markdown("<style>@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=JetBrains+Mono:wght@300;400&display=swap'); html, body, [class*='css'], .stMarkdown, p, div { font-family: 'JetBrains Mono', monospace !important; } .stApp { background-color: #0e1117; color: #e0e0e0; } .jarvis-header { font-family: 'Orbitron', sans-serif !important; font-size: 42px; font-weight: 700; color: #00d4ff; letter-spacing: 5px; text-shadow: 0 0 15px #00d4ffaa; } .jarvis-active-border { border: 2px solid #ff8c00; border-radius: 12px; padding: 20px; background: rgba(22, 27, 34, 0.95); box-shadow: 0 0 25px rgba(255, 140, 0, 0.25); margin-top: 10px; }</style>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SISTEMA DE MEMÓRIA E LEITURA OTIMIZADA
# ---------------------------------------------------------
CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)
JARVIS_ICONE = "https://i.postimg.cc/pL9r8QrW/file-00000000d098720e9f42563f99c6aef6.png"

def obter_essencia_do_codigo():
    """Lê apenas a lógica do código, ignorando o CSS para economizar tokens."""
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            linhas = f.readlines()
            # Retorna apenas as linhas que não são puro CSS/HTML pesado
            return "".join([l for l in linhas if "st.markdown" not in l or "style" not in l])
    except: return "Acesso aos protocolos falhou."

if "chat_atual" not in st.session_state: st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
if "messages" not in st.session_state: st.session_state.messages = []
if "titulo_atual" not in st.session_state: st.session_state.titulo_atual = "SESSÃO INICIAL"

def carregar_chat(chat_id):
    path = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    return {"titulo": "Novo Registro", "messages": []}

def salvar_chat(chat_id, titulo, msgs):
    with open(os.path.join(CHATS_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
        json.dump({"titulo": titulo, "messages": msgs}, f)

# ---------------------------------------------------------
# 3. CORE OS: CONTROLES
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:Orbitron;'>CORE OS</h2>", unsafe_allow_html=True)
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 40)
    humor = st.slider("Humor %", 0, 100, 30)
    if st.button("+ NOVO PROTOCOLO"):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"; st.session_state.messages = []; st.session_state.titulo_atual = "AGUARDANDO..."; st.rerun()

# ---------------------------------------------------------
# 4. PROCESSAMENTO OTIMIZADO (ANTI-BLOQUEIO)
# ---------------------------------------------------------
st.markdown("<div class='jarvis-header'>J.A.R.V.I.S.</div>", unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar=(None if m["role"]=="user" else JARVIS_ICONE)):
        st.markdown(m["content"])

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Comando, Senhor Lincoln..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant", avatar=JARVIS_ICONE):
        response_placeholder = st.empty()
        full_res = ""
        
        # Só anexa a essência do código se necessário
        contexto = ""
        if any(word in prompt.lower() for word in ["código", "script", "atualize", "mude"]):
            contexto = f"\n\nLÓGICA ATUAL DO SISTEMA:\n{obter_essencia_do_codigo()}"

        sys_msg = (
            f"Você é o J.A.R.V.I.S., assistente sofisticado do Senhor Lincoln. "
            f"DIRETRIZ: Seja breve. Resuma o que for útil. NUNCA use parênteses para ações. "
            f"Se solicitado uma mudança, forneça o bloco de código específico ou o script completo de forma otimizada. "
            f"Sarcasmo {sarcasmo}%, Humor {humor}%."
            f"{contexto}"
        )

        try:
            # Enviamos apenas as últimas 3 mensagens para garantir que nunca trave por tamanho
            stream = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages[-3:],
                model="llama-3.1-8b-instant", stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    response_placeholder.markdown(f'<div class="jarvis-active-border">{full_res}█</div>', unsafe_allow_html=True)
            
            response_placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            salvar_chat(st.session_state.chat_atual, st.session_state.titulo_atual, st.session_state.messages)
        except Exception as e: st.error(f"Erro: {e}")
