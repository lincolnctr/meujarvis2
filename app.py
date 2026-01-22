import streamlit as st
from groq import Groq
import os
import json
import uuid
import time

# ---------------------------------------------------------
# 1. CONFIGURAÇÕES E ESTILO
# ---------------------------------------------------------
st.set_page_config(page_title="J.A.R.V.I.S. OS", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    
    .jarvis-active-border {
        border: 2px solid #ff8c00;
        border-radius: 15px;
        padding: 20px;
        background: linear-gradient(145deg, #161b22, #0e1117);
        box-shadow: 0 0 20px rgba(255, 140, 0, 0.4);
        animation: pulse-orange 2s infinite;
        margin-top: 10px;
    }

    @keyframes pulse-orange {
        0% { border-color: #4b1d00; box-shadow: 0 0 5px rgba(75, 29, 0, 0.5); }
        50% { border-color: #ff8c00; box-shadow: 0 0 25px rgba(255, 140, 0, 0.7); }
        100% { border-color: #ffcc33; box-shadow: 0 0 5px rgba(255, 204, 51, 0.5); }
    }

    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .stSlider label { color: #ff8c00 !important; font-family: monospace; }
    .jarvis-log { color: #00d4ff; font-family: 'monospace'; font-size: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. INICIALIZAÇÃO DE ESTADOS (CORREÇÃO DO ERRO)
# ---------------------------------------------------------
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "titulo_atual" not in st.session_state:
    st.session_state.titulo_atual = "Aguardando Comando..."

# ---------------------------------------------------------
# 3. SISTEMA DE ARQUIVOS E MEMÓRIA
# ---------------------------------------------------------
CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)
JARVIS_ICONE = "https://i.postimg.cc/pL9r8QrW/file-00000000d098720e9f42563f99c6aef6.png"

def carregar_chat(chat_id):
    path = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    return {"titulo": "Novo Registro", "messages": []}

def salvar_chat(chat_id, titulo, msgs):
    with open(os.path.join(CHATS_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
        json.dump({"titulo": titulo, "messages": msgs}, f)

# ---------------------------------------------------------
# 4. CORE OS: CONTROLES E REGISTROS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:monospace;'>CORE OS</h2>", unsafe_allow_html=True)
    
    st.subheader("Personalidade")
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 50)
    humor = st.slider("Humor %", 0, 100, 30)
    sinceridade = st.slider("Sinceridade %", 0, 100, 100)
    
    st.markdown("---")
    if st.button("+ Reiniciar Protocolos"):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
        st.session_state.messages = []
        st.session_state.titulo_atual = "Novo Registro"
        st.rerun()

    st.subheader("Registros")
    if os.path.exists(CHATS_DIR):
        for f in sorted(os.listdir(CHATS_DIR), reverse=True):
            cid = f.replace(".json", "")
            dados = carregar_chat(cid)
            col1, col2 = st.columns([0.8, 0.2])
            if col1.button(f"• {dados.get('titulo', 'Sem Título')}", key=f"b_{cid}"):
                st.session_state.chat_atual = cid
                st.session_state.messages = dados['messages']
                st.session_state.titulo_atual = dados.get('titulo', 'Sessão')
                st.rerun()
            if col2.button("🗑️", key=f"d_{cid}"):
                os.remove(os.path.join(CHATS_DIR, f))
                st.rerun()

# ---------------------------------------------------------
# 5. INTERFACE PRINCIPAL
# ---------------------------------------------------------
st.markdown(f"<div class='jarvis-log'>J.A.R.V.I.S. | {st.session_state.titulo_atual}</div>", unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar=(None if m["role"]=="user" else JARVIS_ICONE)):
        st.markdown(m["content"])

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Comando, Senhor Lincoln..."):
    
    # Se for o início, gerar título baseado no primeiro assunto
    if not st.session_state.messages:
        try:
            res_titulo = client.chat.completions.create(
                messages=[{"role": "user", "content": f"Crie um título curto (máx 3 palavras) para este assunto: {prompt}"}],
                model="llama-3.1-8b-instant"
            )
            st.session_state.titulo_atual = res_titulo.choices[0].message.content.replace('"', '')
        except:
            st.session_state.titulo_atual = prompt[:20]

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=JARVIS_ICONE):
        response_placeholder = st.empty()
        full_res = ""
        try:
            sys_msg = f"Você é o J.A.R.V.I.S. Chame de Senhor Lincoln. Sarcasmo {sarcasmo}%, Humor {humor}%, Sinceridade {sinceridade}%."
            stream = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages,
                model="llama-3.1-8b-instant",
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    response_placeholder.markdown(f'<div class="jarvis-active-border">{full_res}█</div>', unsafe_allow_html=True)
            
            response_placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
            # SALVA COM O TÍTULO DO PRIMEIRO ASSUNTO
            salvar_chat(st.session_state.chat_atual, st.session_state.titulo_atual, st.session_state.messages)

        except Exception as e:
            st.error(f"Erro no Core: {e}")
