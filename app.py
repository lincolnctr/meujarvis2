import streamlit as st
from groq import Groq
import os
import json
import uuid

# 1. Configuração da Página
st.set_page_config(page_title="J.A.R.V.I.S. OS", page_icon="🤖", layout="wide")

# 2. CSS Estilizado (Cores frias e chat alinhado)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    h1 { color: #00d4ff; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stChatMessage"] { border-radius: 15px; margin-bottom: 10px; width: 80%; }
    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {
        margin-left: auto; background-color: #1d2b3a; border: 1px solid #00d4ff55;
    }
    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from assistant"]) {
        margin-right: auto; background-color: #161b22; border: 1px solid #30363d;
    }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. Gerenciamento de Memória em Disco
CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR):
    os.makedirs(CHATS_DIR)

def carregar_perfil():
    if os.path.exists("perfil.txt"):
        with open("perfil.txt", "r", encoding="utf-8") as f:
            return f.read()
    return "Lincoln, brasileiro, organizado."

def listar_chats():
    arquivos = [f for f in os.listdir(CHATS_DIR) if f.endswith(".json")]
    return sorted(arquivos, reverse=True)

def salvar_chat(chat_id, mensagens):
    with open(os.path.join(CHATS_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
        json.dump(mensagens, f)

def carregar_chat(chat_id):
    caminho = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# 4. Barra Lateral (Sidebar) - Interface de Novos Chats
st.sidebar.title("Sistemas J.A.R.V.I.S.")

if st.sidebar.button("➕ Novo Chat"):
    novo_id = f"chat_{uuid.uuid4().hex[:6]}"
    st.session_state.chat_atual = novo_id
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Histórico de Chats")

chats_salvos = listar_chats()
for chat_file in chats_salvos:
    id_exibicao = chat_file.replace(".json", "")
    if st.sidebar.button(f"💬 {id_exibicao}", key=id_exibicao):
        st.session_state.chat_atual = id_exibicao
        st.session_state.messages = carregar_chat(id_exibicao)
        st.rerun()

# 5. Inicialização da Sessão
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = "chat_principal"
if "messages" not in st.session_state:
    st.session_state.messages = carregar_chat(st.session_state.chat_atual)

st.title("J.A.R.V.I.S.")
st.caption(f"ID da Sessão: {st.session_state.chat_atual}")

# 6. Conexão Groq
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = "SUA_CHAVE_AQUI"
client = Groq(api_key=api_key)
perfil_contexto = carregar_perfil()

# Exibir conversas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Input e Resposta
if prompt := st.chat_input("Comande, Senhor Lincoln..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            system_prompt = f"Você é o JARVIS. Elegante, técnico e curto. Perfil: {perfil_contexto}. Chame-o de Senhor Lincoln."
            
            full_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
            completion = client.chat.completions.create(messages=full_messages, model="llama-3.1-8b-instant")
            
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            salvar_chat(st.session_state.chat_atual, st.session_state.messages)
        except Exception as e:
            st.error(f"Erro: {e}")
