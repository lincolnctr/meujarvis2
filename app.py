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
# 2. DESIGN: WAVEFORM MINIMALISTA E FLUTUANTE
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }

    /* Waveform flutuando exatamente acima do input */
    .waveform-float {
        position: fixed;
        bottom: 95px; /* Distância exata para não tocar na caixa de texto */
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        height: 35px;
        display: flex;
        align-items: flex-end; /* Nasce de baixo para cima */
        justify-content: center;
        gap: 3px;
        z-index: 9999;
        pointer-events: none; /* Não interfere no clique */
        background: transparent; /* Sem caixa/fundo */
    }

    .bar { width: 3px; border-radius: 1px; transition: 0.1s; }
    
    .bar-idle { height: 3px; background-color: rgba(255, 255, 255, 0.1); }
    
    @keyframes wave-surge {
        0%, 100% { height: 4px; opacity: 0.4; }
        50% { height: 32px; opacity: 1; }
    }

    .bar-active {
        background-color: #ff8c00;
        box-shadow: 0 0 12px #ff8c00aa;
        animation: wave-surge 0.6s infinite ease-in-out;
    }

    /* Variação harmônica das barras */
    .bar:nth-child(odd) { animation-duration: 0.7s; }
    .bar:nth-child(3n) { animation-duration: 0.5s; }

    /* Estilo dos Balões de Chat */
    [data-testid="stChatMessage"] { 
        border-radius: 12px; 
        width: 95% !important; 
        background-color: #161b22;
        border: 1px solid #30363d;
        margin-bottom: 15px;
    }

    /* Espaço extra no final para as mensagens não ficarem atrás do input */
    .main .block-container { padding-bottom: 180px; }

    .jarvis-log { color: #00d4ff; font-family: 'monospace'; font-size: 18px; text-shadow: 0 0 10px #00d4ff55; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. COMPONENTE WAVEFORM (SOMENTE AS BARRAS)
# ---------------------------------------------------------
def render_waveform(active=False):
    status = "bar-active" if active else "bar-idle"
    # 100 barras para cobrir quase toda a extensão horizontal
    bars = "".join([f'<div class="bar {status}"></div>' for _ in range(100)])
    return f'<div class="waveform-float">{bars}</div>'

# ---------------------------------------------------------
# 4. FUNÇÕES DE ARQUIVO
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
# 5. SIDEBAR (REGISTROS)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:monospace;'>CORE OS</h2>", unsafe_allow_html=True)
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 50)
    
    st.markdown("---")
    if st.button("Novo Protocolo"):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
        st.session_state.messages = []
        st.session_state.titulo_atual = "Aguardando..."
        st.rerun()

    st.subheader("Histórico")
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

# Placeholder do Waveform (Sempre fixo embaixo)
wave_placeholder = st.empty()

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar=(MEU_ICONE if m["role"] == "user" else JARVIS_ICONE)):
        st.markdown(m["content"])

# ---------------------------------------------------------
# 7. PROCESSAMENTO GROQ
# ---------------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Insira comando..."):
    # Garante que o waveform apareça como idle antes de começar
    wave_placeholder.markdown(render_waveform(active=False), unsafe_allow_html=True)
    
    if not st.session_state.messages:
        r = client.chat.completions.create(messages=[{"role": "user", "content": f"Resuma em 2 palavras: {prompt}"}], model="llama-3.1-8b-instant")
        st.session_state.titulo_atual = r.choices[0].message.content.strip()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=MEU_ICONE):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=JARVIS_ICONE):
        # ATIVA O WAVEFORM (Laranja)
        wave_placeholder.markdown(render_waveform(active=True), unsafe_allow_html=True)
        
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
            # VOLTA AO ESTADO IDLE (Cinza sutil)
            wave_placeholder.markdown(render_waveform(active=False), unsafe_allow_html=True)
else:
    # Mantém o waveform visível em standby
    wave_placeholder.markdown(render_waveform(active=False), unsafe_allow_html=True)
