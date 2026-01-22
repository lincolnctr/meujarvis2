import streamlit as st
from groq import Groq
import os
import json
import uuid

# 1. Configuração da Página - Forçar Sidebar aberta no carregamento
st.set_page_config(
    page_title="J.A.R.V.I.S. OS", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS Estilizado com Correção da Seta (Sidebar)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; min-width: 250px; }
    
    /* REPOSICIONAMENTO DA SETA NO CELULAR */
    [data-testid="stSidebarCollapsedControl"] {
        background-color: #1d2b3a;
        color: #00d4ff;
        border-radius: 0 10px 10px 0;
        top: 10px; /* Garante que ela não suba demais */
        display: flex !important; /* Força a exibição */
    }

    .jarvis-header { 
        color: #00d4ff; 
        font-family: 'monospace'; 
        font-weight: bold; 
        font-size: 20px; 
        border-bottom: 2px solid #00d4ff; 
        padding-bottom: 10px; 
        margin-bottom: 20px; 
    }

    /* Ajuste para o Título não colidir com a seta */
    .main-title {
        margin-left: 45px; /* Abre espaço para a seta no mobile */
    }

    .stButton>button { width: 100%; border-radius: 5px; background-color: #1d2b3a; color: #00d4ff; border: 1px solid #30363d; text-align: left; }
    
    /* Esconde o header padrão mas mantém os controles necessários */
    header { visibility: hidden; }
    header [data-testid="stSidebarCollapsedControl"] { visibility: visible; }
    
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. Funções de Sistema (Inteligentes)
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
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = json.load(f)
            return conteudo if isinstance(conteudo, dict) else {"titulo": "Protocolo Antigo", "mensagens": conteudo}
    return {"titulo": "Novo Protocolo", "mensagens": []}

def gerar_titulo_ia(primeira_pergunta, client):
    try:
        resp = client.chat.completions.create(
            messages=[{"role": "system", "content": "Gere um título de 2 palavras para o assunto abaixo. Responda apenas as palavras."},
                      {"role": "user", "content": primeira_pergunta}],
            model="llama-3.1-8b-instant"
        )
        return resp.choices[0].message.content.strip()
    except: return "Sessão Ativa"

# 4. Sidebar - Central de Controle
with st.sidebar:
    st.markdown("<div class='jarvis-header'>SISTEMA CORE</div>", unsafe_allow_html=True)
    
    if st.button("⚡ NOVO PROTOCOLO"):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
        st.session_state.messages = []
        st.session_state.titulo_atual = "Aguardando..."
        st.rerun()
    
    st.markdown("---")
    st.subheader("Registros")
    
    arquivos = sorted([f for f in os.listdir(CHATS_DIR) if f.endswith(".json")], reverse=True)
    for chat_file in arquivos:
        c_id = chat_file.replace(".json", "")
        dados = carregar_chat(c_id)
        tit = dados.get('titulo', "Sessão")
        
        # Colunas para Chat e Deletar
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            if st.button(f"📄 {tit}", key=f"btn_{c_id}"):
                st.session_state.chat_atual = c_id
                st.session_state.messages = dados.get('mensagens', [])
                st.session_state.titulo_atual = tit
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{c_id}"):
                os.remove(os.path.join(CHATS_DIR, chat_file))
                st.rerun()

# 5. Interface Principal
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = "sessao_inicial"
    d = carregar_chat("sessao_inicial")
    st.session_state.messages = d['mensagens']
    st.session_state.titulo_atual = d['titulo']

st.markdown(f"<h2 style='color:#00d4ff;'>J.A.R.V.I.S. <span style='color:#fff; font-size:18px;'>| {st.session_state.titulo_atual}</span></h2>", unsafe_allow_html=True)

# 6. Groq
if "GROQ_API_KEY" in st.secrets: api_key = st.secrets["GROQ_API_KEY"]
else: api_key = "SUA_CHAVE_AQUI"
client = Groq(api_key=api_key)
perfil_contexto = carregar_perfil()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Insira comando..."):
    if not st.session_state.messages:
        st.session_state.titulo_atual = gerar_titulo_ia(prompt, client)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            system_prompt = f"Você é o JARVIS. Técnico e direto. Usuário: {perfil_contexto}. Chame de Senhor Lincoln."
            full_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
            completion = client.chat.completions.create(messages=full_messages, model="llama-3.1-8b-instant")
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            salvar_chat(st.session_state.chat_atual, st.session_state.titulo_atual, st.session_state.messages)
        except Exception as e:
            st.error(f"Erro: {e}")
