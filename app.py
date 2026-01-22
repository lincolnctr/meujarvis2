import streamlit as st
from groq import Groq
import os
import json
import uuid
import time

# ---------------------------------------------------------
# 1. CONFIGURAÇÕES DE SISTEMA
# ---------------------------------------------------------
st.set_page_config(page_title="J.A.R.V.I.S. OS", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# ---------------------------------------------------------
# 2. DESIGN: MOLDURA NEON DINÂMICA (APENAS NA RESPOSTA ATIVA)
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }

    /* EFEITO DE BORDA LARANJA MULTI-TOM */
    @keyframes orange-glow {
        0% { border-color: #4b1d00; box-shadow: 0 0 5px #4b1d00; }
        50% { border-color: #ff8c00; box-shadow: 0 0 20px #ff8c00aa; }
        100% { border-color: #ffcc33; box-shadow: 0 0 5px #ffcc33; }
    }

    /* Aplica apenas ao último balão da IA enquanto o placeholder estiver ativo */
    .jarvis-active div[data-testid="stChatMessage"]:has(img[src*="file-00000000d098720e9f42563f99c6aef6"]):last-child {
        border: 2px solid #ff8c00 !important;
        animation: orange-glow 1.5s infinite ease-in-out !important;
        background-color: #1a1f26 !important;
    }

    /* Balões de Chat padrão */
    [data-testid="stChatMessage"] { 
        border-radius: 15px; 
        margin-bottom: 10px;
        border: 1px solid #30363d;
    }

    .jarvis-log { color: #00d4ff; font-family: 'monospace'; font-size: 18px; text-shadow: 0 0 10px #00d4ff55; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. FUNÇÕES DE MEMÓRIA
# ---------------------------------------------------------
CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)
MEU_ICONE = "👤" 
JARVIS_ICONE = "https://i.postimg.cc/pL9r8QrW/file-00000000d098720e9f42563f99c6aef6.png"

def carregar_chat(chat_id):
    caminho = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"titulo": "Novo Protocolo", "messages": []}

def salvar_chat(chat_id, titulo, mensagens):
    with open(os.path.join(CHATS_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
        json.dump({"titulo": titulo, "messages": mensagens}, f)

# ---------------------------------------------------------
# 4. SIDEBAR: CORE OS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:monospace;'>CORE OS</h2>", unsafe_allow_html=True)
    
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 50)
    humor = st.slider("Humor %", 0, 100, 30)
    sinceridade = st.slider("Sinceridade %", 0, 100, 100)
    
    st.markdown("---")
    if st.button("+ Novo Protocolo"):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
        st.session_state.messages = []
        st.rerun()

    st.subheader("Registros")
    if os.path.exists(CHATS_DIR):
        for f_name in sorted(os.listdir(CHATS_DIR), reverse=True):
            c_id = f_name.replace(".json", "")
            dados = carregar_chat(c_id)
            cols = st.columns([0.8, 0.2])
            if cols[0].button(f"• {dados.get('titulo', 'Sessão')}", key=f"b_{c_id}"):
                st.session_state.chat_atual = c_id
                st.session_state.messages = dados['messages']
                st.rerun()
            if cols[1].button("🗑️", key=f"d_{c_id}"):
                os.remove(os.path.join(CHATS_DIR, f_name))
                st.rerun()

# ---------------------------------------------------------
# 5. INTERFACE
# ---------------------------------------------------------
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
    st.session_state.messages = []

st.markdown(f"<div class='jarvis-log'>J.A.R.V.I.S. | PROTOCOLO ATIVO</div>", unsafe_allow_html=True)

# Container principal para permitir injeção de classe dinâmica
chat_container = st.container()

with chat_container:
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar=(MEU_ICONE if m["role"] == "user" else JARVIS_ICONE)):
            st.markdown(m["content"])

# ---------------------------------------------------------
# 6. RESPOSTA REATIVA
# ---------------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Comando, Senhor Lincoln..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container:
        with st.chat_message("user", avatar=MEU_ICONE):
            st.markdown(prompt)

    with chat_container:
        # Criamos um wrapper que ativa o CSS de moldura
        st.markdown('<div class="jarvis-active">', unsafe_allow_html=True)
        with st.chat_message("assistant", avatar=JARVIS_ICONE):
            try:
                sys_msg = f"Você é o J.A.R.V.I.S. Chame de Senhor Lincoln. Sarcasmo {sarcasmo}%, Humor {humor}%, Sinceridade {sinceridade}%."
                full_history = [{"role": "system", "content": sys_msg}] + st.session_state.messages
                response = client.chat.completions.create(messages=full_history, model="llama-3.1-8b-instant", stream=True)

                def stream_text():
                    for chunk in response:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                            time.sleep(0.01)

                full_res = st.write_stream(stream_text())
                st.session_state.messages.append({"role": "assistant", "content": full_res})
                salvar_chat(st.session_state.chat_atual, prompt[:15], st.session_state.messages)
            finally:
                st.markdown('</div>', unsafe_allow_html=True)
