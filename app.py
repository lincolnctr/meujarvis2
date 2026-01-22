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
# 2. DESIGN: WAVEFORM CINÉTICO (LARANJA STARK)
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }

    /* Container do Visualizador de Áudio */
    .waveform-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 3px;
        height: 100px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #30363d;
    }

    .bar {
        width: 5px;
        border-radius: 3px;
        transition: all 0.2s ease;
    }

    /* ESTADO: STANDBY (Cinza e estático) */
    .bar-idle {
        height: 4px;
        background-color: #30363d;
    }

    /* ESTADO: TRANSMISSÃO (Laranja e pulsante) */
    @keyframes wave-bounce {
        0%, 100% { height: 8px; }
        50% { height: 70px; }
    }

    .bar-active {
        background-color: #ff4b1f; /* Laranja Vibrante */
        box-shadow: 0 0 15px #ff4b1f66;
        animation: wave-bounce 0.6s infinite ease-in-out;
    }

    /* Variação de ritmo entre as barras */
    .bar:nth-child(odd) { animation-duration: 0.5s; }
    .bar:nth-child(even) { animation-duration: 0.8s; }
    .bar:nth-child(3n) { animation-duration: 0.4s; }

    [data-testid="stChatMessage"] { 
        border-radius: 12px; 
        width: 95% !important; 
        max-width: 100% !important; 
        background-color: #161b22;
        border: 1px solid #30363d;
        animation: fadeIn 0.6s ease-out;
    }
    
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    .jarvis-log { color: #00d4ff; font-family: 'monospace'; font-size: 18px; padding-left: 50px; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. COMPONENTE VISUAL DO WAVEFORM
# ---------------------------------------------------------
def render_waveform(is_talking=False):
    status = "bar-active" if is_talking else "bar-idle"
    # Criamos 15 barras para um visual robusto
    bars = "".join([f'<div class="bar {status}"></div>' for _ in range(15)])
    return f'<div class="waveform-container">{bars}</div>'

# ---------------------------------------------------------
# 4. MEMÓRIA E PERSISTÊNCIA
# ---------------------------------------------------------
CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)
MEU_ICONE = "👤" 
JARVIS_ICONE = "https://i.postimg.cc/pL9r8QrW/file-00000000d098720e9f42563f99c6aef6.png"

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
# 5. BARRA LATERAL (CENTRO DE COMANDO)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:monospace;'>CORE OS</h2>", unsafe_allow_html=True)
    
    aba_config, aba_audio = st.tabs(["PERSONALIDADE", "AUDIO CORE"])
    
    with aba_config:
        sarcasmo = st.slider("Sarcasmo %", 0, 100, 50)
        humor = st.slider("Humor %", 0, 100, 30)
        sinceridade = st.slider("Sinceridade %", 0, 100, 100)
        
    with aba_audio:
        st.write("Monitor de Frequência Visual")
        # Espaço dinâmico do Waveform
        waveform_placeholder = st.empty()
        waveform_placeholder.markdown(render_waveform(is_talking=False), unsafe_allow_html=True)
        st.caption("Status: Standby (Sem sinal de áudio)")

    st.markdown("---")
    if st.button("Limpar Terminal"):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------
# 6. INTERFACE PRINCIPAL
# ---------------------------------------------------------
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = "sessao_inicial"
    d = carregar_chat("sessao_inicial")
    st.session_state.messages = d['messages']

st.markdown(f"<div class='jarvis-log'>J.A.R.V.I.S. | FREQUÊNCIA ATIVA</div>", unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar=(MEU_ICONE if m["role"] == "user" else JARVIS_ICONE)):
        st.markdown(m["content"])

# ---------------------------------------------------------
# 7. MOTOR REATIVO (SINCRO COM WAVEFORM)
# ---------------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Aguardando comando, Senhor Lincoln..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=MEU_ICONE):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=JARVIS_ICONE):
        # LIGA O WAVEFORM (Efeito Visual de Transmissão)
        waveform_placeholder.markdown(render_waveform(is_talking=True), unsafe_allow_html=True)
        
        try:
            sys_msg = f"Você é o J.A.R.V.I.S. Chame de Senhor Lincoln. Sarcasmo {sarcasmo}%. Humor {humor}%."
            history = [{"role": "system", "content": sys_msg}] + st.session_state.messages
            
            response = client.chat.completions.create(messages=history, model="llama-3.1-8b-instant", stream=True)

            def stream_logic():
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                        time.sleep(0.01)

            full_response = st.write_stream(stream_logic())
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            salvar_chat(st.session_state.chat_atual, "Protocolo Ativo", st.session_state.messages)
            
        finally:
            # DESLIGA O WAVEFORM (Retorno ao silêncio visual)
            waveform_placeholder.markdown(render_waveform(is_talking=False), unsafe_allow_html=True)
