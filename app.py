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
# 2. DESIGN: LINHA DE ENERGIA LARANJA (FIXO NO TOPO DO INPUT)
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    
    /* A LINHA DE ENERGIA */
    .jarvis-energy-line {
        position: fixed;
        bottom: 85px; /* Posição exata acima da caixa de texto */
        left: 0;
        width: 100%;
        height: 5px;
        z-index: 9999999; /* Força ficar por cima de tudo */
        transition: all 0.5s ease;
    }

    /* Animação de Fluxo Laranja */
    @keyframes flow-orange {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }

    /* ESTADO ATIVO: Tons de Laranja (Claro, Médio, Escuro) */
    .energy-active {
        background: linear-gradient(90deg, #4b1d00, #ff4500, #ff8c00, #ffcc33, #ff8c00, #ff4500, #4b1d00);
        background-size: 200% auto;
        animation: flow-orange 1s linear infinite;
        box-shadow: 0 -8px 20px rgba(255, 69, 0, 0.6);
        opacity: 1;
    }

    /* ESTADO IDLE: Linha quase invisível */
    .energy-idle {
        background: rgba(255, 140, 0, 0.1);
        box-shadow: none;
        opacity: 0.3;
        height: 2px;
    }

    /* Espaçamento para o chat não ficar colado na linha */
    .main .block-container { padding-bottom: 160px; }
    
    /* Customização dos balões */
    [data-testid="stChatMessage"] { 
        border-radius: 12px; 
        background-color: #161b22;
        border: 1px solid #30363d;
    }
    .jarvis-log { color: #00d4ff; font-family: 'monospace'; font-size: 18px; text-shadow: 0 0 10px #00d4ff55; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. COMPONENTE DE RENDERIZAÇÃO
# ---------------------------------------------------------
def render_energy(active=False):
    status = "energy-active" if active else "energy-idle"
    return f'<div class="jarvis-energy-line {status}"></div>'

# ---------------------------------------------------------
# 4. FUNÇÕES DE MEMÓRIA
# ---------------------------------------------------------
CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)
MEU_ICONE = "👤" 
JARVIS_ICONE = "https://i.postimg.cc/pL9r8QrW/file-00000000d098720e9f42563f99c6aef6.png"

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
# 5. SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:monospace;'>CORE OS</h2>", unsafe_allow_html=True)
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 50)
    
    if st.button("Novo Protocolo"):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
        st.session_state.messages = []
        st.session_state.titulo_atual = "Aguardando..."
        st.rerun()

    st.subheader("Registros")
    if os.path.exists(CHATS_DIR):
        for f_name in sorted(os.listdir(CHATS_DIR), reverse=True):
            c_id = f_name.replace(".json", "")
            dados = carregar_chat(c_id)
            if st.button(f"• {dados['titulo']}", key=f"btn_{c_id}"):
                st.session_state.chat_atual = c_id
                st.session_state.messages = dados['messages']
                st.session_state.titulo_atual = dados['titulo']
                st.rerun()

# ---------------------------------------------------------
# 6. INTERFACE DE CHAT
# ---------------------------------------------------------
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = "sessao_inicial"
    d = carregar_chat("sessao_inicial")
    st.session_state.messages, st.session_state.titulo_atual = d['messages'], d['titulo']

st.markdown(f"<div class='jarvis-log'>J.A.R.V.I.S. | {st.session_state.titulo_atual}</div>", unsafe_allow_html=True)

# Renderiza histórico
for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar=(MEU_ICONE if m["role"] == "user" else JARVIS_ICONE)):
        st.markdown(m["content"])

# Placeholder da Linha (Renderizada estrategicamente aqui)
energy_line_placeholder = st.empty()

# ---------------------------------------------------------
# 7. MOTOR REATIVO
# ---------------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Comando..."):
    # Inicializa a linha em idle
    energy_line_placeholder.markdown(render_energy(active=False), unsafe_allow_html=True)
    
    if not st.session_state.messages:
        st.session_state.titulo_atual = "Sessão Ativa"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=MEU_ICONE):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=JARVIS_ICONE):
        # ATIVA A LINHA LARANJA NO TOPO DO INPUT
        energy_line_placeholder.markdown(render_energy(active=True), unsafe_allow_html=True)
        
        try:
            sys_msg = f"Você é o J.A.R.V.I.S. Chame de Senhor Lincoln. Sarcasmo {sarcasmo}%."
            history = [{"role": "system", "content": sys_msg}] + st.session_state.messages
            response = client.chat.completions.create(messages=history, model="llama-3.1-8b-instant", stream=True)

            def fluidez():
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                        time.sleep(0.01)

            full_res = st.write_stream(fluidez())
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            salvar_chat(st.session_state.chat_atual, st.session_state.titulo_atual, st.session_state.messages)
            
        finally:
            # VOLTA AO ESTADO IDLE
            energy_line_placeholder.markdown(render_energy(active=False), unsafe_allow_html=True)
else:
    # Garante que a linha esteja visível em standby
    energy_line_placeholder.markdown(render_energy(active=False), unsafe_allow_html=True)
