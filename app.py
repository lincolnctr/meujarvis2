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

# 2. CSS Estilizado
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .jarvis-title { color: #00d4ff; font-family: 'monospace'; letter-spacing: 4px; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #1d2b3a; color: #00d4ff; border: 1px solid #30363d; text-align: left; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. Funções de Sistema (Com Tratamento de Erro de Versão)
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
            # Se for o formato novo (dicionário com título)
            if isinstance(conteudo, dict):
                return conteudo
            # Se for o formato antigo (apenas uma lista de mensagens)
            else:
                return {"titulo": "Protocolo Antigo", "mensagens": conteudo}
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

# 4. Sidebar
st.sidebar.markdown("<h1 class='jarvis-title'>CORE</h1>", unsafe_allow_html=True)

if st.sidebar.button("⚡ NOVO PROTOCOLO"):
    novo_id = f"chat_{uuid.uuid4().hex[:6]}"
    st.session_state.chat_atual = novo_id
    st.session_state.messages = []
    st.session_state.titulo_atual = "Aguardando comando..."
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Logs de Memória")

if os.path.exists(CHATS_DIR):
    arquivos = sorted([f for f in os.listdir(CHATS_DIR) if f.endswith(".json")], reverse=True)
    for chat_file in arquivos:
        c_id = chat_file.replace(".json", "")
        dados = carregar_chat(c_id)
        nome_exibicao = dados.get('titulo', "Protocolo Antigo")
        
        if st.sidebar.button(f"ID: {nome_exibicao}", key=c_id):
            st.session_state.chat_atual = c_id
            st.session_state.messages = dados.get('mensagens', [])
            st.session_state.titulo_atual = nome_exibicao
            st.rerun()

# 5. Inicialização da Sessão
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = "sessao_inicial"
    dados_init = carregar_chat("sessao_inicial")
    st.session_state.messages = dados_init['mensagens']
    st.session_state.titulo_atual = dados_init['titulo']

st.markdown(f"<h3 style='color:#00d4ff;'>J.A.R.V.I.S. > {st.session_state.titulo_atual}</h3>", unsafe_allow_html=True)

# 6. Groq e Perfil
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
            system_prompt = f"Você é o JARVIS. Elegante, técnico e curto. Contexto: {perfil_contexto}. Chame-o de Senhor Lincoln."
            full_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
            completion = client.chat.completions.create(messages=full_messages, model="llama-3.1-8b-instant")
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            salvar_chat(st.session_state.chat_atual, st.session_state.titulo_atual, st.session_state.messages)
        except Exception as e:
            st.error(f"Erro: {e}")
