import streamlit as st
from groq import Groq
import os
import json
import uuid

# 1. Configuração da Página - Forçando o menu aberto e layout mobile
st.set_page_config(
    page_title="J.A.R.V.I.S. OS", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS Avançado para Ícones e Estética
st.markdown("""
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
    <style>
    .stApp { background-color: #0e1117; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    h1 { color: #00d4ff; font-family: 'Segoe UI', sans-serif; letter-spacing: 2px; }
    
    /* Estilização dos Botões da Sidebar */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #1d2b3a;
        color: #00d4ff;
        border: 1px solid #30363d;
        transition: 0.3s;
        text-align: left;
        padding-left: 15px;
    }
    .stButton>button:hover {
        border-color: #00d4ff;
        background-color: #253341;
    }

    /* Balões de Chat */
    [data-testid="stChatMessage"] { border-radius: 15px; margin-bottom: 10px; width: 85%; }
    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {
        margin-left: auto; background-color: #1d2b3a; border: 1px solid #00d4ff55;
    }
    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from assistant"]) {
        margin-right: auto; background-color: #161b22; border: 1px solid #30363d;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. Funções de Sistema
CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)

def carregar_perfil():
    if os.path.exists("perfil.txt"):
        with open("perfil.txt", "r", encoding="utf-8") as f: return f.read()
    return "Lincoln, brasileiro, organizado."

def salvar_chat(chat_id, titulo, mensagens):
    dados = {"titulo": titulo, "mensagens": mensagens}
    with open(os.path.join(CHATS_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
        json.dump(dados, f)

def carregar_chat(chat_id):
    caminho = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f: return json.load(f)
    return {"titulo": "Novo Chat", "mensagens": []}

def gerar_titulo_ia(primeira_pergunta, client):
    try:
        resp = client.chat.completions.create(
            messages=[{"role": "system", "content": "Gere um título curto de no máximo 3 palavras para um chat que começa com a pergunta abaixo. Responda APENAS o título."},
                      {"role": "user", "content": primeira_pergunta}],
            model="llama-3.1-8b-instant"
        )
        return resp.choices[0].message.content.replace('"', '')
    except: return "Chat Gravado"

# 4. Sidebar - Gerenciamento de Chats
st.sidebar.markdown("<h2 style='color:#00d4ff;'>CORE OS</h2>", unsafe_allow_html=True)

if st.sidebar.button("+ NOVO PROTOCOLO"):
    novo_id = f"chat_{uuid.uuid4().hex[:6]}"
    st.session_state.chat_atual = novo_id
    st.session_state.messages = []
    st.session_state.titulo_atual = "Novo Chat"
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Arquivos de Memória")

arquivos = sorted([f for f in os.listdir(CHATS_DIR) if f.endswith(".json")], reverse=True)
for chat_file in arquivos:
    c_id = chat_file.replace(".json", "")
    dados = carregar_chat(c_id)
    # Usando um ícone de terminal para os botões
    if st.sidebar.button(f"📄 {dados['titulo']}", key=c_id):
        st.session_state.chat_atual = c_id
        st.session_state.messages = dados['mensagens']
        st.session_state.titulo_atual = dados['titulo']
        st.rerun()

# 5. Inicialização
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = "chat_principal"
    dados_init = carregar_chat("chat_principal")
    st.session_state.messages = dados_init['mensagens']
    st.session_state.titulo_atual = dados_init['titulo']

st.title("J.A.R.V.I.S.")
st.caption(f"Protocolo Ativo: {st.session_state.titulo_atual}")

# 6. Conexão Groq
if "GROQ_API_KEY" in st.secrets: api_key = st.secrets["GROQ_API_KEY"]
else: api_key = "SUA_CHAVE_AQUI"
client = Groq(api_key=api_key)
perfil_contexto = carregar_perfil()

# Exibir histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Lógica de Chat e Nomenclatura Automática
if prompt := st.chat_input("Comande, Senhor Lincoln..."):
    # Se for a primeira mensagem, gera um título
    if not st.session_state.messages:
        st.session_state.titulo_atual = gerar_titulo_ia(prompt, client)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            system_prompt = f"Você é o JARVIS. Elegante, técnico e curto. Contexto: {perfil_contexto}. Chame-o de Senhor Lincoln."
            full_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
            
            completion = client.chat.completions.create(messages=full_messages, model="llama-3.1-8b-instant")
            response = completion.choices[0].message.content
            st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            salvar_chat(st.session_state.chat_atual, st.session_state.titulo_atual, st.session_state.messages)
        except Exception as e:
            st.error(f"Erro: {e}")
