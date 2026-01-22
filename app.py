import streamlit as st
from groq import Groq
import os
import json
import uuid

# 1. Configuração da Página
st.set_page_config(
    page_title="J.A.R.V.I.S. OS", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS Estilizado (Seta Visível e Título Ajustado)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    
    /* Forçar a seta a aparecer no mobile */
    button[kind="header"] {
        color: #00d4ff !important;
        background-color: rgba(0, 212, 255, 0.1) !important;
        border-radius: 50% !important;
    }

    .jarvis-log {
        color: #00d4ff; font-family: 'monospace'; font-size: 20px; font-weight: bold;
        padding-left: 50px; margin-top: -10px;
    }

    .stButton>button {
        width: 100%; border-radius: 5px; background-color: #1d2b3a; color: #00d4ff; 
        border: 1px solid #30363d; text-align: left; margin-bottom: 5px;
    }

    header { background-color: rgba(0,0,0,0) !important; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 3. Funções de Memória
CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)

def carregar_perfil():
    if os.path.exists("perfil.txt"):
        with open("perfil.txt", "r", encoding="utf-8") as f: return f.read()
    return "Lincoln, brasileiro, organizado."

def salvar_chat(chat_id, titulo, mensagens):
    with open(os.path.join(CHATS_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
        json.dump({"titulo": titulo, "mensagens": mensagens}, f)

def carregar_chat(chat_id):
    caminho = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            c = json.load(f)
            return c if isinstance(c, dict) else {"titulo": "Antigo", "mensagens": c}
    return {"titulo": "Novo Protocolo", "mensagens": []}

def gerar_titulo_ia(pergunta, client):
    try:
        r = client.chat.completions.create(
            messages=[{"role": "system", "content": "Título de 2 palavras para o tema. Apenas as palavras."},
                      {"role": "user", "content": pergunta}],
            model="llama-3.1-8b-instant"
        )
        return r.choices[0].message.content.strip()
    except: return "Sessão"

# 4. Sidebar
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:monospace;'>CORE OS</h2>", unsafe_allow_html=True)
    if st.button("⚡ NOVO PROTOCOLO"):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
        st.session_state.messages = []
        st.session_state.titulo_atual = "Aguardando..."
        st.rerun()
    st.markdown("---")
    if os.path.exists(CHATS_DIR):
        for f_name in sorted(os.listdir(CHATS_DIR), reverse=True):
            c_id = f_name.replace(".json", "")
            dados = carregar_chat(c_id)
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                if st.button(f"📄 {dados['titulo']}", key=f"b_{c_id}"):
                    st.session_state.chat_atual = c_id
                    st.session_state.messages = dados['mensagens']
                    st.session_state.titulo_atual = dados['titulo']
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"d_{c_id}"):
                    os.remove(os.path.join(CHATS_DIR, f_name))
                    st.rerun()

# 5. Estado da Sessão
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = "sessao_inicial"
    d = carregar_chat("sessao_inicial")
    st.session_state.messages = d['mensagens']
    st.session_state.titulo_atual = d['titulo']

st.markdown(f"<div class='jarvis-log'>J.A.R.V.I.S. | {st.session_state.titulo_atual}</div>", unsafe_allow_html=True)

# 6. Groq e Chat
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
perfil = carregar_perfil()

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Comando..."):
    if not st.session_state.messages:
        st.session_state.titulo_atual = gerar_titulo_ia(prompt, client)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # PROMPT ULTRA SECO E DIRETO
            sys = f"Você é o JARVIS. Contexto: {perfil}. Regras: Responda apenas o necessário, no máximo 2 frases. Seja seco e técnico. Chame de Senhor Lincoln no final."
            
            full_m = [{"role": "system", "content": sys}] + st.session_state.messages
            res = client.chat.completions.create(messages=full_m, model="llama-3.1-8b-instant")
            content = res.choices[0].message.content
            
            if content:
                st.markdown(content)
                st.session_state.messages.append({"role": "assistant", "content": content})
                salvar_chat(st.session_state.chat_atual, st.session_state.titulo_atual, st.session_state.messages)
            else:
                st.error("Erro: Resposta vazia.")
        except Exception as e:
            st.error(f"Erro: {e}")
