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
# 2. DESIGN: WAVEFORM PANORÂMICO FIXO NO RODAPÉ
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }

    /* Waveform fixado acima da caixa de input */
    .waveform-footer {
        position: fixed;
        bottom: 80px; /* Ajustado para ficar logo acima do input do Streamlit */
        left: 0;
        right: 0;
        height: 40px;
        background: rgba(14, 17, 23, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 3px;
        padding: 0 20px;
        z-index: 999;
        backdrop-filter: blur(5px);
    }

    .bar { width: 3px; border-radius: 1px; transition: 0.15s; }
    
    .bar-idle { height: 4px; background-color: #30363d; }
    
    @keyframes wave-flow {
        0%, 100% { height: 6px; opacity: 0.5; }
        50% { height: 30px; opacity: 1; }
    }

    .bar-active {
        background-color: #ff8c00;
        box-shadow: 0 0 10px #ff8c0088;
        animation: wave-flow 0.7s infinite ease-in-out;
    }

    /* Waveform ocupa quase toda a largura com delays progressivos */
    .bar:nth-child(5n) { animation-delay: 0.1s; }
    .bar:nth-child(3n) { animation-delay: 0.2s; }
    .bar:nth-child(2n) { animation-delay: 0.3s; }

    [data-testid="stChatMessage"] { 
        border-radius: 12px; 
        width: 95% !important; 
        background-color: #161b22;
        border: 1px solid #30363d;
        margin-bottom: 10px;
    }

    /* Padding extra no final do chat para o waveform não cobrir a última mensagem */
    .stChatFloatingInputContainer { background-color: #0e1117 !important; }
    .main .block-container { padding-bottom: 150px; }

    .jarvis-log { color: #00d4ff; font-family: 'monospace'; font-size: 18px; text-shadow: 0 0 10px #00d4ff55; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. COMPONENTE WAVEFORM PANORÂMICO
# ---------------------------------------------------------
def render_waveform(active=False):
    status = "bar-active" if active else "bar-idle"
    # 80 barras para cruzar a tela
    bars = "".join([f'<div class="bar {status}"></div>' for _ in range(80)])
    return f'<div class="waveform-footer">{bars}</div>'

# ---------------------------------------------------------
# 4. FUNÇÕES DE APOIO
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
        for f_name in sorted(os.listdir(CHATS_DIR), reverse=True):
            c_id = f_name.replace(".json", "")
            dados = carregar_chat(c_id)
            if st.button(f"• {dados['titulo']}", key=f"btn_{c_id}"):
                st.session_state.chat_atual = c_id
                st.session_state.messages = dados['messages']
                st.session_state.titulo_atual = dados['titulo']
                st.rerun()

# ---------------------------------------------------------
# 6. INTERFACE
# ---------------------------------------------------------
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = "sessao_inicial"
    d = carregar_chat("sessao_inicial")
    st.session_state.messages, st.session_state.titulo_atual = d['messages'], d['titulo']

st.markdown(f"<div class='jarvis-log'>J.A.R.V.I.S. | {st.session_state.titulo_atual}</div>", unsafe_allow_html=True)

# Placeholder Fixo para o Waveform
wave_placeholder = st.empty()

# Render das mensagens
for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar=(MEU_ICONE if m["role"] == "user" else JARVIS_ICONE)):
        st.markdown(m["content"])

# ---------------------------------------------------------
# 7. MOTOR REATIVO
# ---------------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Insira comando..."):
    # Estado inicial do Waveform (Cinza)
    wave_placeholder.markdown(render_waveform(active=False), unsafe_allow_html=True)
    
    if not st.session_state.messages:
        r = client.chat.completions.create(messages=[{"role": "user", "content": f"Resuma em 2 palavras: {prompt}"}], model="llama-3.1-8b-instant")
        st.session_state.titulo_atual = r.choices[0].message.content.strip()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=MEU_ICONE):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=JARVIS_ICONE):
        # LIGA WAVEFORM PANORÂMICO LARANJA
        wave_placeholder.markdown(render_waveform(active=True), unsafe_allow_html=True)
        
        try:
            sys_msg = f"Você é o J.A.R.V.I.S. Chame de Senhor Lincoln. Sarcasmo {sarcasmo}%, Humor {humor}%."
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
            # DESLIGA WAVEFORM (VOLTA AO CINZA)
            wave_placeholder.markdown(render_waveform(active=False), unsafe_allow_html=True)
else:
    # Garante que o waveform apareça mesmo sem input novo
    wave_placeholder.markdown(render_waveform(active=False), unsafe_allow_html=True)
