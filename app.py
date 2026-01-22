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
# 2. DESIGN: BACKGROUND HOLOGRÁFICO E INTERFACE
# ---------------------------------------------------------
HOLOG_IMG = "https://i.postimg.cc/Vv5fPMJs/image-5.jpg"

st.markdown(f"""
    <style>
    /* Configuração do Background Geral */
    .stApp {{
        background-color: #0e1117;
    }}

    /* Container do Holograma no Fundo */
    .hologram-bg {{
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 600px;
        height: 600px;
        background-image: url('{HOLOG_IMG}');
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        opacity: 0.05; /* Bem sutil no fundo */
        z-index: -1;
        transition: all 1s ease-in-out;
        border-radius: 50%;
    }}

    /* Efeito quando o J.A.R.V.I.S. está pensando (chamado via script) */
    .thinking-active {{
        opacity: 0.2 !important;
        filter: drop-shadow(0 0 30px #00d4ff) hue-rotate(0deg);
        animation: spin 20s linear infinite, glow 2s infinite ease-in-out;
    }}

    @keyframes spin {{ 100% {{ transform: translate(-50%, -50%) rotate(360deg); }} }}
    @keyframes glow {{ 
        0%, 100% {{ filter: drop-shadow(0 0 20px #00d4ff); }} 
        50% {{ filter: drop-shadow(0 0 50px #00d4ff); }} 
    }}

    /* Estilo dos Balões de Chat */
    [data-testid="stChatMessage"] {{ 
        border-radius: 12px; 
        margin-bottom: 15px; 
        width: 95% !important; 
        max-width: 100% !important; 
        background-color: rgba(22, 27, 34, 0.8) !important; /* Transparência para ver o fundo */
        backdrop-filter: blur(5px);
    }}

    .jarvis-log {{ color: #00d4ff; font-family: 'monospace'; font-size: 18px; padding-left: 50px; }}
    [data-testid="stSidebar"] {{ background-color: #161b22; }}
    </style>
    
    <div id="hologram" class="hologram-bg"></div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. FUNÇÕES DE MEMÓRIA
# ---------------------------------------------------------
CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)

MEU_ICONE = "👤" 
JARVIS_ICONE = "https://i.postimg.cc/pL9r8QrW/file-00000000d098720e9f42563f99c6aef6.png"

def carregar_perfil():
    return open("perfil.txt", "r").read().strip() if os.path.exists("perfil.txt") else "Lincoln"

def carregar_chat(chat_id):
    caminho = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(caminho):
        with open(caminho, "r") as f:
            c = json.load(f)
            return {"titulo": c.get('titulo', "Sessão"), "messages": c.get('messages', [])}
    return {"titulo": "Novo Protocolo", "messages": []}

def salvar_chat(chat_id, titulo, mensagens):
    with open(os.path.join(CHATS_DIR, f"{chat_id}.json"), "w") as f:
        json.dump({"titulo": titulo, "messages": mensagens}, f)

# ---------------------------------------------------------
# 4. PAINEL LATERAL
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:monospace;'>CORE OS</h2>", unsafe_allow_html=True)
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 50)
    
    if st.button("Novo Protocolo..."):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------
# 5. INTERFACE DE CHAT
# ---------------------------------------------------------
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = "sessao_inicial"
    d = carregar_chat("sessao_inicial")
    st.session_state.messages = d['messages']
    st.session_state.titulo_atual = d['titulo']

st.markdown(f"<div class='jarvis-log'>J.A.R.V.I.S. | PROTOCOLO ATIVO</div>", unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar=(MEU_ICONE if m["role"] == "user" else JARVIS_ICONE)):
        st.markdown(m["content"])

# ---------------------------------------------------------
# 6. MOTOR E ANIMAÇÃO REATIVA
# ---------------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Comando..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=MEU_ICONE):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=JARVIS_ICONE):
        # ATIVA O HOLOGRAMA NO FUNDO (Aumenta opacidade e brilha)
        st.markdown("<script>document.getElementById('hologram').classList.add('thinking-active');</script>", unsafe_allow_html=True)
        
        try:
            full_m = [{"role": "system", "content": f"Você é o JARVIS. Senhor Lincoln seu dono. Sarcasmo {sarcasmo}%."}] + st.session_state.messages
            response = client.chat.completions.create(messages=full_m, model="llama-3.1-8b-instant", stream=True)

            def typing():
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                        time.sleep(0.01)

            content = st.write_stream(typing())
            st.session_state.messages.append({"role": "assistant", "content": content})
            salvar_chat(st.session_state.chat_atual, "Chat Ativo", st.session_state.messages)
            
        finally:
            # DESATIVA O HOLOGRAMA NO FUNDO
            st.markdown("<script>document.getElementById('hologram').classList.remove('thinking-active');</script>", unsafe_allow_html=True)
