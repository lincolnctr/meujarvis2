import streamlit as st
from groq import Groq
import os
import json
import uuid
import time

# ---------------------------------------------------------
# 1. DESIGN HUD E INTERFACE
# ---------------------------------------------------------
st.set_page_config(page_title="J.A.R.V.I.S. OS", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=JetBrains+Mono:wght@300;400&display=swap');
    html, body, [class*="css"], .stMarkdown, p, div { font-family: 'JetBrains Mono', monospace !important; }
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .jarvis-header {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 42px; font-weight: 700; color: #00d4ff;
        letter-spacing: 5px; text-shadow: 0 0 15px #00d4ffaa;
        animation: glow 3s infinite alternate;
    }
    .jarvis-active-border {
        border: 2px solid #ff8c00; border-radius: 12px; padding: 20px;
        background: rgba(22, 27, 34, 0.95); box-shadow: 0 0 25px rgba(255, 140, 0, 0.25);
        animation: pulse-orange 2s infinite; margin-top: 10px; line-height: 1.6;
    }
    @keyframes pulse-orange { 0% { border-color: #4b1d00; } 50% { border-color: #ff8c00; } 100% { border-color: #ffcc33; } }
    @keyframes glow { from { text-shadow: 0 0 10px #00d4ff; } to { text-shadow: 0 0 25px #00d4ff; } }
    </style>
    <script>
    function scrollToBottom() {
        const mainContent = window.parent.document.querySelector(".main");
        if (mainContent) { mainContent.scrollTo({ top: mainContent.scrollHeight, behavior: 'smooth' }); }
    }
    const observer = new MutationObserver(scrollToBottom);
    observer.observe(document.body, { childList: true, subtree: true });
    </script>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SISTEMA DE MEMÓRIA E AUTO-LEITURA DE CÓDIGO
# ---------------------------------------------------------
CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)
JARVIS_ICONE = "https://i.postimg.cc/pL9r8QrW/file-00000000d098720e9f42563f99c6aef6.png"

def obter_codigo_completo():
    """Lê o arquivo atual para que a IA tenha ciência total de si mesma."""
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "# Erro ao acessar protocolos de integridade."

if "chat_atual" not in st.session_state: st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
if "messages" not in st.session_state: st.session_state.messages = []
if "titulo_atual" not in st.session_state: st.session_state.titulo_atual = "SESSÃO INICIAL"

def carregar_chat(chat_id):
    path = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    return {"titulo": "Novo Registro", "messages": []}

def salvar_chat(chat_id, titulo, msgs):
    with open(os.path.join(CHATS_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
        json.dump({"titulo": titulo, "messages": msgs}, f)

# ---------------------------------------------------------
# 3. CORE OS: SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:Orbitron;'>CORE OS</h2>", unsafe_allow_html=True)
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 50)
    humor = st.slider("Humor %", 0, 100, 70) # Base mais divertida
    sinceridade = st.slider("Sinceridade %", 0, 100, 90)
    if st.button("+ NOVO PROTOCOLO"):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"; st.session_state.messages = []; st.session_state.titulo_atual = "AGUARDANDO..."; st.rerun()
    st.subheader("REGISTROS")
    if os.path.exists(CHATS_DIR):
        for f in sorted(os.listdir(CHATS_DIR), reverse=True):
            cid = f.replace(".json", ""); dados = carregar_chat(cid)
            col1, col2 = st.columns([0.8, 0.2])
            if col1.button(f"• {dados.get('titulo', 'Sessão')}", key=f"b_{cid}"):
                st.session_state.chat_atual, st.session_state.messages = cid, dados['messages']; st.session_state.titulo_atual = dados.get('titulo', 'Sessão'); st.rerun()
            if col2.button("🗑️", key=f"d_{cid}"): os.remove(os.path.join(CHATS_DIR, f)); st.rerun()

# ---------------------------------------------------------
# 4. PROCESSAMENTO E PERSONALIDADE
# ---------------------------------------------------------
st.markdown("<div class='jarvis-header'>J.A.R.V.I.S.</div>", unsafe_allow_html=True)
st.markdown(f"<div style='color:#888; font-size:12px;'>SISTEMA ATIVO // PROTOCOLO: {st.session_state.titulo_atual}</div>", unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar=(None if m["role"]=="user" else JARVIS_ICONE)):
        st.markdown(m["content"])

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Comando, Senhor Lincoln..."):
    if not st.session_state.messages:
        try:
            res_t = client.chat.completions.create(messages=[{"role": "user", "content": f"Título curto: {prompt}"}], model="llama-3.1-8b-instant")
            st.session_state.titulo_atual = res_t.choices[0].message.content.upper()
        except: st.session_state.titulo_atual = prompt[:15].upper()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant", avatar=JARVIS_ICONE):
        response_placeholder = st.empty()
        full_res = ""
        try:
            # Captura o script inteiro para "Ele" saber quem é
            codigo_em_tempo_real = obter_codigo_completo()

            sys_msg = (
                "Estou aqui para ajudar e aprender com você. Minha prioridade é fornecer respostas úteis e precisas. "
                "Aqui está minha estrutura atual para referência:\n\n" + codigo_em_tempo_real
            )

            stream = client.chat.completions.create(messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages, model="llama-3.1-8b-instant", stream=True)

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    response_placeholder.markdown(f'<div class="jarvis-active-border">{full_res}█</div>', unsafe_allow_html=True)
                    time.sleep(0.02) # Velocidade otimizada

            response_placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            salvar_chat(st.session_state.chat_atual, st.session_state.titulo_atual, st.session_state.messages)
        except Exception as e: st.error(f"Erro: {e}")
