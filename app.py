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
# 2. DESIGN: WAVEFORM NO TOPO E INTERFACE EXPANDIDA
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }

    /* Waveform Fixado no Topo */
    .waveform-top-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
        height: 60px;
        background: rgba(22, 27, 34, 0.8);
        border-radius: 15px;
        border: 1px solid #00d4ff33;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }

    .bar { width: 4px; border-radius: 2px; transition: 0.2s; }
    
    .bar-idle { height: 6px; background-color: #4a4a4a; }
    
    @keyframes wave-surge {
        0%, 100% { height: 10px; }
        50% { height: 45px; }
    }

    .bar-active {
        background-color: #ff8c00;
        box-shadow: 0 0 15px #ff8c00aa;
        animation: wave-surge 0.6s infinite ease-in-out;
    }

    /* Delays para as barras */
    .bar:nth-child(2n) { animation-delay: 0.1s; }
    .bar:nth-child(3n) { animation-delay: 0.2s; }
    .bar:nth-child(4n) { animation-delay: 0.3s; }

    /* Balões de Chat Full-Width */
    [data-testid="stChatMessage"] { 
        border-radius: 12px; 
        width: 95% !important; 
        max-width: 100% !important; 
        background-color: #161b22;
        border: 1px solid #30363d;
    }

    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {
        margin-left: auto !important;
        background-color: #1d2b3a;
        border: 1px solid #00d4ff33;
    }

    .jarvis-log { color: #00d4ff; font-family: 'monospace'; font-size: 18px; text-shadow: 0 0 10px #00d4ff; margin-bottom: 10px; }
    
    header { background-color: rgba(0,0,0,0) !important; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. COMPONENTE VISUAL
# ---------------------------------------------------------
def render_waveform(active=False):
    status = "bar-active" if active else "bar-idle"
    # 25 barras para um visual de cinema
    bars = "".join([f'<div class="bar {status}"></div>' for _ in range(25)])
    return f'<div class="waveform-top-container">{bars}</div>'

# ---------------------------------------------------------
# 4. MEMÓRIA E PERSISTÊNCIA (CHATS)
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
        with open(caminho, "r", encoding="utf-8") as f:
            c = json.load(f)
            return {"titulo": c.get('titulo', "Sessão"), "messages": c.get('messages', [])}
    return {"titulo": "Novo Protocolo", "messages": []}

def salvar_chat(chat_id, titulo, mensagens):
    with open(os.path.join(CHATS_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
        json.dump({"titulo": titulo, "messages": mensagens}, f)

# ---------------------------------------------------------
# 5. BARRA LATERAL (REGISTROS E PERSONALIDADE)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:monospace;'>CORE OS</h2>", unsafe_allow_html=True)
    
    st.subheader("Personalidade")
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 50)
    humor = st.slider("Humor %", 0, 100, 30)
    sinceridade = st.slider("Sinceridade %", 0, 100, 100)
    
    st.markdown("---")
    if st.button("Novo Protocolo..."):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
        st.session_state.messages = []
        st.session_state.titulo_atual = "Aguardando..."
        st.rerun()

    st.subheader("Registros")
    if os.path.exists(CHATS_DIR):
        arquivos = sorted(os.listdir(CHATS_DIR), reverse=True)
        for f_name in arquivos:
            c_id = f_name.replace(".json", "")
            dados = carregar_chat(c_id)
            if st.button(f"• {dados['titulo']}", key=f"btn_{c_id}"):
                st.session_state.chat_atual = c_id
                st.session_state.messages = dados['messages']
                st.session_state.titulo_atual = dados['titulo']
                st.rerun()

# ---------------------------------------------------------
# 6. INTERFACE PRINCIPAL
# ---------------------------------------------------------
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = "sessao_inicial"
    d = carregar_chat("sessao_inicial")
    st.session_state.messages = d['messages']
    st.session_state.titulo_atual = d['titulo']

# Log e Waveform fixo no topo
st.markdown(f"<div class='jarvis-log'>J.A.R.V.I.S. | {st.session_state.titulo_atual}</div>", unsafe_allow_html=True)
wave_placeholder = st.empty()
wave_placeholder.markdown(render_waveform(active=False), unsafe_allow_html=True)

# Container de Mensagens
for m in st.session_state.messages:
    icone = MEU_ICONE if m["role"] == "user" else JARVIS_ICONE
    with st.chat_message(m["role"], avatar=icone):
        st.markdown(m["content"])

# ---------------------------------------------------------
# 7. MOTOR REATIVO
# ---------------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
perfil = carregar_perfil()

if prompt := st.chat_input("Insira comando..."):
    # Título automático se for a primeira mensagem
    if not st.session_state.messages:
        r = client.chat.completions.create(
            messages=[{"role": "user", "content": f"Resuma em 2 palavras: {prompt}"}],
            model="llama-3.1-8b-instant"
        )
        st.session_state.titulo_atual = r.choices[0].message.content.strip()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=MEU_ICONE):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=JARVIS_ICONE):
        # ATIVA O WAVEFORM LARANJA
        wave_placeholder.markdown(render_waveform(active=True), unsafe_allow_html=True)
        
        try:
            sys_msg = f"Você é o J.A.R.V.I.S. dono {perfil}. Sarcasmo {sarcasmo}%, Humor {humor}%, Sinceridade {sinceridade}%. Seja direto, chame de Senhor Lincoln."
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
            # VOLTA O WAVEFORM PARA CINZA
            wave_placeholder.markdown(render_waveform(active=False), unsafe_allow_html=True)
