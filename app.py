import streamlit as st
from groq import Groq
import os
import json
import uuid

# ---------------------------------------------------------
# 1. CONFIGURAÇÕES DE SISTEMA (NOME E ESTADO INICIAL)
# ---------------------------------------------------------
st.set_page_config(
    page_title="J.A.R.V.I.S. OS", # <--- NOME NA ABA DO NAVEGADOR
    page_icon="🤖",               # <--- ÍCONE NA ABA DO NAVEGADOR
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. DESIGN E CORES (INTERFACE VISUAL)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* COR DE FUNDO DO APP */
    .stApp { background-color: #0b0c0d; } 

    /* BARRA LATERAL (SIDEBAR) */
    [data-testid="stSidebar"] { 
        background-color: #16181a;      /* <--- COR DO FUNDO DA BARRA */
        border-right: 1px solid #30363d; /* <--- COR DA BORDA DA BARRA */
    }

    /* BOTÃO DE ABRIR SIDEBAR (SETA NO MOBILE) */
    button[kind="header"] {
        color: #00d4ff !important;      /* <--- COR DA SETA */
        background-color: rgba(0, 212, 255, 0.1) !important;
    }

    /* LOGO / TÍTULO PRINCIPAL NO TOPO */
    .jarvis-log {
        color: #1b578f;                 /* <--- COR DO NOME J.A.R.V.I.S. */
        font-family: 'monospace';
        font-size: 20px;
        font-weight: bold;
        padding-left: 50px;
    }

    /* BOTÕES GERAIS (NOVO CHAT E REGISTROS) */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #1d2b3a;      /* <--- COR DO FUNDO DO BOTÃO */
        color: #00d4ff;                 /* <--- COR DO TEXTO/ÍCONE DO BOTÃO */
        border: 1px solid #30363d;      /* <--- COR DA BORDA DO BOTÃO */
        text-align: left;
    }
    
    header { background-color: rgba(0,0,0,0) !important; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. PROCESSAMENTO DE DADOS (CÉREBRO)
# ---------------------------------------------------------
CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)

def carregar_perfil():
    if os.path.exists("perfil.txt"):
        with open("perfil.txt", "r", encoding="utf-8") as f: return f.read()
    return "Lincoln, organizado."

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

# ---------------------------------------------------------
# 4. PAINEL DE CONTROLE LATERAL
# ---------------------------------------------------------
with st.sidebar:
    # TÍTULO DA BARRA LATERAL
    st.markdown("<h2 style='color:#1b578f; font-family:monospace;'>SISTEMA CORE</h2>", unsafe_allow_html=True)
    
    # AJUSTES DE PERSONALIDADE (SLIDERS)
    st.subheader("Personalidade")
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 50)
    sinceridade = st.slider("Sinceridade %", 0, 100, 100)
    humor = st.slider("Humor %", 0, 100, 30)
    
    st.markdown("---")
    
    # BOTÃO PARA CRIAR NOVO CHAT
    if st.button("Novo Protocolo"): # <--- MUDAR NOME DO BOTÃO AQUI
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
        st.session_state.messages = []
        st.session_state.titulo_atual = "Aguardando..."
        st.rerun()
    
    st.subheader("Registros") # <--- TÍTULO DA LISTA DE CHATS
    if os.path.exists(CHATS_DIR):
        for f_name in sorted(os.listdir(CHATS_DIR), reverse=True):
            c_id = f_name.replace(".json", "")
            dados = carregar_chat(c_id)
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                # ÍCONE E TÍTULO DO CHAT SALVO
                if st.button(f"• {dados['titulo']}", key=f"b_{c_id}"):
                    st.session_state.chat_atual = c_id
                    st.session_state.messages = dados['mensagens']
                    st.session_state.titulo_atual = dados['titulo']
                    st.rerun()
            with col2:
                # ÍCONE DE DELETAR
                if st.button("🗑️", key=f"d_{c_id}"):
                    os.remove(os.path.join(CHATS_DIR, f_name))
                    st.rerun()

# ---------------------------------------------------------
# 5. TELA DE CHAT PRINCIPAL
# ---------------------------------------------------------
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = "sessao_inicial"
    d = carregar_chat("sessao_inicial")
    st.session_state.messages = d['mensagens']
    st.session_state.titulo_atual = d['titulo']

# TÍTULO QUE APARECE NO TOPO DO CHAT
st.markdown(f"<div class='jarvis-log'>J.A.R.V.I.S. | {st.session_state.titulo_atual}</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. MOTOR DE INTELIGÊNCIA (GROQ)
# ---------------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
perfil = carregar_perfil()

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# CAIXA DE TEXTO ONDE VOCÊ DIGITA
if prompt := st.chat_input("Insira comando..."): 
    if not st.session_state.messages:
        # GERAR TÍTULO AUTOMÁTICO
        r = client.chat.completions.create(
            messages=[{"role": "system", "content": "2 palavras de título."}, {"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant"
        )
        st.session_state.titulo_atual = r.choices[0].message.content.strip()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # LÓGICA DE PERSONALIDADE NO PROMPT
            sys_prompt = f"Você é o JARVIS. Sarcasmo {sarcasmo}%, Humor {humor}%, Sinceridade {sinceridade}%. Responda curto, informal e técnico. Chame de Senhor Lincoln."
            
            full_m = [{"role": "system", "content": sys_prompt}] + st.session_state.messages
            res = client.chat.completions.create(messages=full_m, model="llama-3.1-8b-instant")
            content = res.choices[0].message.content
            
            st.markdown(content)
            st.session_state.messages.append({"role": "assistant", "content": content})
            salvar_chat(st.session_state.chat_atual, st.session_state.titulo_atual, st.session_state.messages)
            
        except Exception as e:
            st.error(f"Erro: {e}")
