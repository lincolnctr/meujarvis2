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
# 2. DESIGN: EFEITOS DE LUZ NEON (SEM IMAGENS)
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }

    /* Efeito de Luz nas Bordas da Tela (Vignette Neon) */
    @keyframes pulseEnergy {
        0% { box-shadow: inset 0 0 20px #00d4ff22; }
        50% { box-shadow: inset 0 0 60px #00d4ff55; }
        100% { box-shadow: inset 0 0 20px #00d4ff22; }
    }

    /* Quando a IA está pensando, a tela inteira brilha levemente */
    .thinking-aura {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        pointer-events: none;
        z-index: 9999;
        animation: pulseEnergy 1.5s infinite ease-in-out;
        border: 2px solid #00d4ff33;
    }

    /* Balões de Chat com Glow Futurista */
    [data-testid="stChatMessage"] { 
        border-radius: 12px; 
        margin-bottom: 15px; 
        width: 95% !important; 
        max-width: 100% !important; 
        transition: 0.5s;
        border: 1px solid #30363d;
    }

    /* Balão do J.A.R.V.I.S. com brilho interno */
    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from assistant"]) {
        background-color: #161b22;
        box-shadow: 0 0 10px #00d4ff11;
    }

    .jarvis-log {
        color: #00d4ff;
        font-family: 'monospace';
        font-size: 18px;
        padding: 10px 0 20px 50px;
        text-shadow: 0 0 10px #00d4ff;
    }

    /* Alinhamento */
    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {
        margin-left: auto !important;
        background-color: #1d2b3a;
        border: 1px solid #00d4ff33;
    }

    header { background-color: rgba(0,0,0,0) !important; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. MEMÓRIA E PERFIL
# ---------------------------------------------------------
CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)

MEU_ICONE = "👤" 
JARVIS_ICONE = "https://i.postimg.cc/pL9r8QrW/file-00000000d098720e9f42563f99c6aef6.png"

def carregar_perfil():
    if os.path.exists("perfil.txt"):
        with open("perfil.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    return "Lincoln, proprietário do sistema."

def carregar_chat(chat_id):
    caminho = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            c = json.load(f)
            return {"titulo": c.get('titulo', "Sessão"), "messages": c.get('messages', [])}
    return {"titulo": "Novo Protocolo", "messages": []}

def salvar_chat(chat_id, titulo, mensagens):
    with open(os.path.join(CHATS_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
        json.dump({"titulo": titulo, "messages": mensagens}, f)

# ---------------------------------------------------------
# 4. PAINEL LATERAL (CORE OS RESTAURADO)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:monospace;'>CORE OS</h2>", unsafe_allow_html=True)
    
    st.subheader("Personalidade")
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 50)
    sinceridade = st.slider("Sinceridade %", 0, 100, 100)
    humor = st.slider("Humor %", 0, 100, 30)
    
    st.markdown("---")
    if st.button("Novo Protocolo..."):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
        st.session_state.messages = []
        st.session_state.titulo_atual = "Aguardando..."
        st.rerun()

    st.subheader("Registros")
    if os.path.exists(CHATS_DIR):
        for f_name in sorted(os.listdir(CHATS_DIR), reverse=True):
            c_id = f_name.replace(".json", "")
            dados = carregar_chat(c_id)
            if st.button(f"• {dados['titulo']}", key=f"b_{c_id}"):
                st.session_state.chat_atual = c_id
                st.session_state.messages = dados['messages']
                st.session_state.titulo_atual = dados['titulo']
                st.rerun()

# ---------------------------------------------------------
# 5. INTERFACE DE CHAT
# ---------------------------------------------------------
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = "sessao_inicial"
    d = carregar_chat("sessao_inicial")
    st.session_state.messages = d['messages']
    st.session_state.titulo_atual = d['titulo']

st.markdown(f"<div class='jarvis-log'>J.A.R.V.I.S. | {st.session_state.titulo_atual}</div>", unsafe_allow_html=True)

# Placeholder para o efeito de luz (Aura)
aura_placeholder = st.empty()

for m in st.session_state.messages:
    icone = MEU_ICONE if m["role"] == "user" else JARVIS_ICONE
    with st.chat_message(m["role"], avatar=icone):
        st.markdown(m["content"])

# ---------------------------------------------------------
# 6. MOTOR COM EFEITO DE LUZ ATIVO
# ---------------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
perfil_data = carregar_perfil()

if prompt := st.chat_input("Comando..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=MEU_ICONE):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=JARVIS_ICONE):
        # ATIVA A LUZ NEON NA TELA
        aura_placeholder.markdown('<div class="thinking-aura"></div>', unsafe_allow_html=True)
        
        try:
            sys_prompt = f"Você é o J.A.R.V.I.S. Chame de Senhor Lincoln. Sarcasmo {sarcasmo}%, Humor {humor}%, Sinceridade {sinceridade}%."
            full_m = [{"role": "system", "content": sys_prompt}] + st.session_state.messages
            
            response = client.chat.completions.create(messages=full_m, model="llama-3.1-8b-instant", stream=True)

            def fluidez():
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                        time.sleep(0.01)

            content = st.write_stream(fluidez())
            
            st.session_state.messages.append({"role": "assistant", "content": content})
            salvar_chat(st.session_state.chat_atual, st.session_state.titulo_atual, st.session_state.messages)
            
        finally:
            # DESLIGA A LUZ NEON
            aura_placeholder.empty()
