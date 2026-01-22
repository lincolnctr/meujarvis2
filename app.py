import streamlit as st
from groq import Groq
import os
import json
import uuid
import time
import shutil

# ---------------------------------------------------------
# 1. CONFIGURAÇÕES DE SISTEMA
# ---------------------------------------------------------
st.set_page_config(page_title="J.A.R.V.I.S. OS", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# ---------------------------------------------------------
# 2. DESIGN: INTERFACE STARK & LINHA DE ENERGIA SUPERIOR
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    
    /* LINHA DE ENERGIA LARANJA - FIXADA ACIMA DO INPUT */
    .jarvis-energy-line {
        position: fixed;
        bottom: 80px; /* Ajuste milimétrico para ficar acima da caixa */
        left: 0;
        width: 100%;
        height: 4px;
        z-index: 999999;
        transition: all 0.4s ease;
    }

    @keyframes energy-flow {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }

    .energy-active {
        background: linear-gradient(90deg, #4b1d00, #ff4500, #ff8c00, #ffcc33, #ff8c00, #ff4500, #4b1d00);
        background-size: 200% auto;
        animation: energy-flow 1.2s linear infinite;
        box-shadow: 0 -10px 20px rgba(255, 69, 0, 0.5);
    }

    .energy-idle {
        background: rgba(255, 140, 0, 0.1);
        height: 2px;
    }

    /* CUSTOMIZAÇÃO SIDEBAR E CHAT */
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    [data-testid="stChatMessage"] { border-radius: 12px; background-color: #161b22; border: 1px solid #30363d; margin-bottom: 10px; }
    .main .block-container { padding-bottom: 160px; }
    .jarvis-log { color: #00d4ff; font-family: 'monospace'; font-size: 18px; text-shadow: 0 0 10px #00d4ff55; }
    
    /* Botão de Deletar Estilizado */
    .stButton>button { width: 100%; border-radius: 5px; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. FUNÇÕES DE SUPORTE (ARQUIVOS E MEMÓRIA)
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

def deletar_todos_chats():
    if os.path.exists(CHATS_DIR):
        shutil.rmtree(CHATS_DIR)
        os.makedirs(CHATS_DIR)
    st.session_state.messages = []
    st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
    st.rerun()

# ---------------------------------------------------------
# 4. CORE OS (BARRA LATERAL)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:monospace;'>CORE OS</h2>", unsafe_allow_html=True)
    
    # MODOS DE PERSONALIDADE RESTAURADOS
    st.subheader("Configurações de IA")
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 50)
    humor = st.slider("Humor %", 0, 100, 30)
    sinceridade = st.slider("Sinceridade %", 0, 100, 100)
    
    st.markdown("---")
    if st.button("Novo Protocolo"):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
        st.session_state.messages = []
        st.rerun()

    st.subheader("Registros Salvos")
    if os.path.exists(CHATS_DIR):
        for f_name in sorted(os.listdir(CHATS_DIR), reverse=True):
            c_id = f_name.replace(".json", "")
            dados = carregar_chat(c_id)
            if st.button(f"• {dados['titulo']}", key=f"btn_{c_id}"):
                st.session_state.chat_atual = c_id
                st.session_state.messages = dados['messages']
                st.rerun()

    st.markdown("---")
    if st.button("🗑️ Deletar Todos os Chats", type="secondary"):
        deletar_todos_chats()

# ---------------------------------------------------------
# 5. INTERFACE DE CHAT
# ---------------------------------------------------------
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = "sessao_inicial"
    d = carregar_chat("sessao_inicial")
    st.session_state.messages = d['messages']

st.markdown(f"<div class='jarvis-log'>J.A.R.V.I.S. | PROTOCOLO ATIVO</div>", unsafe_allow_html=True)

# Placeholder da Linha de Energia (Renderizada no topo para fixação)
energy_placeholder = st.empty()

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar=(MEU_ICONE if m["role"] == "user" else JARVIS_ICONE)):
        st.markdown(m["content"])

# ---------------------------------------------------------
# 6. MOTOR REATIVO
# ---------------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Comando, Senhor Lincoln..."):
    # Estado standby da linha
    energy_placeholder.markdown(f'<div class="jarvis-energy-line energy-idle"></div>', unsafe_allow_html=True)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=MEU_ICONE):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=JARVIS_ICONE):
        # ATIVA LINHA LARANJA ACIMA DO INPUT
        energy_placeholder.markdown(f'<div class="jarvis-energy-line energy-active"></div>', unsafe_allow_html=True)
        
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
            
            # Título automático baseado no contexto
            titulo_chat = prompt[:20] + "..."
            salvar_chat(st.session_state.chat_atual, titulo_chat, st.session_state.messages)
            
        finally:
            # VOLTA AO ESTADO IDLE
            energy_placeholder.markdown(f'<div class="jarvis-energy-line energy-idle"></div>', unsafe_allow_html=True)
else:
    energy_placeholder.markdown(f'<div class="jarvis-energy-line energy-idle"></div>', unsafe_allow_html=True)
