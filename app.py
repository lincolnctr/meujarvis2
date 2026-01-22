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

# 2. CSS Ultra-Refinado para Mobile
st.markdown("""
    <style>
    /* Fundo principal */
    .stApp { background-color: #0e1117; }
    
    /* Estilização da Sidebar */
    [data-testid="stSidebar"] { 
        background-color: #161b22; 
        border-right: 1px solid #30363d; 
    }

    /* FORÇAR A SETA A APARECER E FICAR NA COR CERTA */
    button[kind="header"] {
        color: #00d4ff !important;
        background-color: rgba(0, 212, 255, 0.1) !important;
        border-radius: 50% !important;
    }

    /* Ajuste do Título para não bater na seta */
    .jarvis-log {
        color: #00d4ff;
        font-family: 'monospace';
        font-size: 22px;
        font-weight: bold;
        padding-left: 50px; /* Abre espaço para a seta no mobile */
        margin-top: -10px;
    }

    /* Botões de Chat na Lateral */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #1d2b3a;
        color: #00d4ff;
        border: 1px solid #30363d;
        text-align: left;
        margin-bottom: 5px;
    }

    /* Esconde apenas a barra cinza, mas mantém os botões de controle */
    header {
        background-color: rgba(0,0,0,0) !important;
        border-bottom: none !important;
    }
    
    footer {visibility: hidden;}
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

# 4. Sidebar
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:monospace;'>CORE OS</h2>", unsafe_allow_html=True)
    
    if st.button("⚡ NOVO PROTOCOLO"):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
        st.session_state.messages = []
        st.session_state.titulo_atual = "Aguardando..."
        st.rerun()
    
    st.markdown("---")
    
    arquivos = sorted([f for f in os.listdir(CHATS_DIR) if f.endswith(".json")], reverse=True)
    for chat_file in arquivos:
        c_id = chat_file.replace(".json", "")
        dados = carregar_chat(c_id)
        tit = dados.get('titulo', "Sessão")
        
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

st.markdown(f"<div class='jarvis-log'>J.A.R.V.I.S. | {st.session_state.titulo_atual}</div>", unsafe_allow_html=True)

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
            # PROTOCOLO DE RESPOSTA CURTA ATIVADO
            system_prompt = f"""
            Você é o JARVIS. 
            CONTEXTO: {perfil_contexto}.
            REGRA DE OURO: Responda de forma extremamente curta, técnica e seca. 
            - Proibido dizer "Olá", "Senhor Lincoln, como posso ajudar?", "Estou à disposição" ou similares.
            - Responda APENAS o que foi perguntado. Se for uma confirmação, diga apenas "Confirmado" ou "Procedimento concluído".
            - Use no máximo duas frases por resposta.
            - Sempre chame o usuário de Senhor Lincoln no final da resposta.
            """
            
            full_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
            completion = client.chat.completions.create(messages=full_messages, model="llama-3.1-8b-instant")
            # ... restante do código ...
        except Exception as e:
            st.error(f"Erro: {e}")
