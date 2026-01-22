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
# 2. DESIGN: MOLDURA REATIVA E INTERFACE
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    
    /* Animação de Fluxo Laranja para as Bordas */
    @keyframes border-flow {
        0% { border-image-source: linear-gradient(90deg, #4b1d00, #ff4500, #ff8c00, #ffcc33); }
        50% { border-image-source: linear-gradient(180deg, #ffcc33, #ff8c00, #ff4500, #4b1d00); }
        100% { border-image-source: linear-gradient(270deg, #4b1d00, #ff4500, #ff8c00, #ffcc33); }
    }

    /* Estilo para a mensagem da IA quando ATIVA (Gerando) */
    .jarvis-response-active {
        border: 2px solid;
        border-image-slice: 1;
        border-image-source: linear-gradient(90deg, #ff4500, #ffcc33);
        animation: border-flow 2s linear infinite;
        box-shadow: 0 0 15px rgba(255, 69, 0, 0.4);
        padding: 15px;
        border-radius: 10px;
        background-color: #161b22;
    }

    /* Balão padrão da IA (Estático) */
    div[data-testid="stChatMessage"]:has(img[src*="file-00000000d098720e9f42563f99c6aef6"]) {
        border: 1px solid #ff8c0033;
        transition: all 0.5s ease;
    }

    /* Sidebar e Botões de Deletar */
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .chat-entry { display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px; }
    .del-btn { color: #ff4b1f; cursor: pointer; font-size: 14px; }
    
    .jarvis-log { color: #00d4ff; font-family: 'monospace'; font-size: 18px; text-shadow: 0 0 10px #00d4ff55; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. FUNÇÕES DE MEMÓRIA (INDIVIDUALIZADA)
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

def deletar_chat_especifico(chat_id):
    caminho = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(caminho):
        os.remove(caminho)
    if st.session_state.get("chat_atual") == chat_id:
        st.session_state.messages = []
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
    st.rerun()

# ---------------------------------------------------------
# 4. SIDEBAR: CORE OS & PERSONALIDADE
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:monospace;'>CORE OS</h2>", unsafe_allow_html=True)
    
    st.subheader("Personalidade")
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 50)
    humor = st.slider("Humor %", 0, 100, 30)
    sinceridade = st.slider("Sinceridade %", 0, 100, 100)
    
    st.markdown("---")
    if st.button("+ Novo Protocolo"):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
        st.session_state.messages = []
        st.rerun()

    st.subheader("Registros de Memória")
    if os.path.exists(CHATS_DIR):
        for f_name in sorted(os.listdir(CHATS_DIR), reverse=True):
            c_id = f_name.replace(".json", "")
            dados = carregar_chat(c_id)
            
            # Layout de linha com botão de deletar individual
            col_chat, col_del = st.columns([0.8, 0.2])
            with col_chat:
                if st.button(f"• {dados['titulo'][:15]}", key=f"btn_{c_id}"):
                    st.session_state.chat_atual = c_id
                    st.session_state.messages = dados['messages']
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"del_{c_id}"):
                    deletar_chat_especifico(c_id)

# ---------------------------------------------------------
# 5. INTERFACE PRINCIPAL
# ---------------------------------------------------------
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
    st.session_state.messages = []

st.markdown(f"<div class='jarvis-log'>J.A.R.V.I.S. | MOLDURA REATIVA</div>", unsafe_allow_html=True)

# Container para as mensagens
for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar=(MEU_ICONE if m["role"] == "user" else JARVIS_ICONE)):
        st.markdown(m["content"])

# ---------------------------------------------------------
# 6. MOTOR REATIVO COM MOLDURA DINÂMICA
# ---------------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Comando, Senhor Lincoln..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=MEU_ICONE):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=JARVIS_ICONE):
        # Aplicamos a classe de animação na moldura via container
        with st.container():
            st.markdown('<div class="jarvis-response-active">', unsafe_allow_html=True)
            
            try:
                sys_msg = f"Você é o J.A.R.V.I.S. Chame de Senhor Lincoln. Sarcasmo {sarcasmo}%, Humor {humor}%, Sinceridade {sinceridade}%."
                history = [{"role": "system", "content": sys_msg}] + st.session_state.messages
                response = client.chat.completions.create(messages=history, model="llama-3.1-8b-instant", stream=True)

                def fluidez():
                    for chunk in response:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                            time.sleep(0.01)

                full_res = st.write_stream(fluidez())
                st.session_state.messages.append({"role": "assistant", "content": full_res})
                
                # Gera um título curto para o arquivo
                titulo = prompt[:15]
                salvar_chat(st.session_state.chat_atual, titulo, st.session_state.messages)
                
            finally:
                st.markdown('</div>', unsafe_allow_html=True)
