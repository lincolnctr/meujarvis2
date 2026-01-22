import streamlit as st
from groq import Groq
import os
import json
import uuid

# ---------------------------------------------------------
# 1. CONFIGURAÇÕES DE SISTEMA
# ---------------------------------------------------------
st.set_page_config(
    page_title="J.A.R.V.I.S. OS", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. DESIGN E PERSONALIZAÇÃO (CORES E ALINHAMENTO)
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; } 
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }

    /* AJUSTE DOS BALÕES DE MENSAGEM */
    [data-testid="stChatMessage"] { border-radius: 15px; margin-bottom: 10px; width: 85%; }

    /* BALÃO DO USUÁRIO (LINCOLN) - DIREITA */
    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {
        margin-left: auto !important;
        background-color: #1d2b3a; /* <--- COR DO SEU BALÃO */
        border: 1px solid #00d4ff55;
    }

    /* BALÃO DA IA (JARVIS) - ESQUERDA */
    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from assistant"]) {
        margin-right: auto !important;
        background-color: #161b22; /* <--- COR DO MEU BALÃO */
        border: 1px solid #30363d;
    }

    /* ESTILO DO TÍTULO E BOTÕES */
    button[kind="header"] { color: #00d4ff !important; background-color: rgba(0, 212, 255, 0.1) !important; border-radius: 50% !important; }
    .jarvis-log { color: #00d4ff; font-family: 'monospace'; font-size: 20px; font-weight: bold; padding-left: 50px; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #1d2b3a; color: #00d4ff; border: 1px solid #30363d; text-align: left; }
    
    header { background-color: rgba(0,0,0,0) !important; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. MEMÓRIA E PERFIL
# ---------------------------------------------------------
CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)

def carregar_perfil():
    if os.path.exists("perfil.txt"):
        with open("perfil.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    return "Lincoln, proprietário do sistema."

def carregar_chat(chat_id):
    caminho = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            c = json.load(f)
            # Compatibilidade com nomes antigos de chaves
            mensagens = c.get('messages', c.get('mensagens', []))
            return {"titulo": c.get('titulo', "Sessão"), "messages": mensagens}
    return {"titulo": "Novo Protocolo", "messages": []}

def salvar_chat(chat_id, titulo, mensagens):
    with open(os.path.join(CHATS_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
        json.dump({"titulo": titulo, "messages": mensagens}, f)

# ---------------------------------------------------------
# 4. PAINEL LATERAL
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:monospace;'>CORE OS</h2>", unsafe_allow_html=True)
    
    st.subheader("Personalidade")
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 50)
    sinceridade = st.slider("Sinceridade %", 0, 100, 100)
    humor = st.slider("Humor %", 0, 100, 30)
    
    st.markdown("---")
    if st.button("⚡ NOVO PROTOCOLO"):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
        st.session_state.messages = []
        st.session_state.titulo_atual = "Aguardando..."
        st.rerun()

    st.subheader("Registros")
    if os.path.exists(CHATS_DIR):
        for f_name in sorted(os.listdir(CHATS_DIR), reverse=True):
            c_id = f_name.replace(".json", "")
            dados = carregar_chat(c_id)
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                if st.button(f"📄 {dados['titulo']}", key=f"b_{c_id}"):
                    st.session_state.chat_atual = c_id
                    st.session_state.messages = dados['messages']
                    st.session_state.titulo_atual = dados['titulo']
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"d_{c_id}"):
                    os.remove(os.path.join(CHATS_DIR, f_name))
                    st.rerun()

# ---------------------------------------------------------
# 5. INTERFACE DE CHAT
# ---------------------------------------------------------
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = "sessao_inicial"
    d = carregar_chat("sessao_inicial")
    st.session_state.messages = d['messages']
    st.session_state.titulo_atual = d['titulo']

st.markdown(f"<div class='jarvis-log'>J.A.R.V.I.S. | {st.session_state.titulo_atual}</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. MOTOR JARVIS (GROQ)
# ---------------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
dados_perfil = carregar_perfil()

# EXIBIÇÃO COM AVATARES PERSONALIZÁVEIS
for m in st.session_state.messages:
    # SINALIZADOR: Altere o emoji abaixo para mudar seu ícone ou o meu
    icone = "ჲ" if m["role"] == "user" else "🤖" 
    with st.chat_message(m["role"], avatar=icone):
        st.markdown(m["content"])

if prompt := st.chat_input("Comando..."):
    if not st.session_state.messages:
        r = client.chat.completions.create(
            messages=[{"role": "user", "content": f"Resuma em 2 palavras: {prompt}"}],
            model="llama-3.1-8b-instant"
        )
        st.session_state.titulo_atual = r.choices[0].message.content.strip()

    st.session_state.messages.append({"role": "user", "content": prompt})
    # SINALIZADOR: Avatar do Lincoln aqui
    with st.chat_message("user", avatar="👤"): 
        st.markdown(prompt)

    # SINALIZADOR: Avatar do JARVIS aqui
    with st.chat_message("assistant", avatar="🤖"): 
        try:
            sys_prompt = f"""
            Você é o J.A.R.V.I.S., a inteligência artificial pessoal do Senhor Lincoln.
            DADOS DO PROPRIETÁRIO: {dados_perfil}.

            DIRETRIZES DE COMUNICAÇÃO:
            - NÃO use tópicos ou listas para falar sobre o Senhor Lincoln. 
            - Fale de forma natural, orgânica e informal, como um braço direito.
            - Se ele perguntar o que você sabe, responda em parágrafos curtos: "Você é o Lincoln, mora em São Paulo...".
            - NUNCA mencione Abraham Lincoln ou política americana.

            PERSONALIDADE ATUAL:
            Sarcasmo {sarcasmo}% | Humor {humor}% | Sinceridade {sinceridade}%
            Chame-o sempre de Senhor Lincoln. Máximo 3 frases.
            """
            
            full_m = [{"role": "system", "content": sys_prompt}] + st.session_state.messages
            res = client.chat.completions.create(messages=full_m, model="llama-3.1-8b-instant")
            content = res.choices[0].message.content
            
            st.markdown(content)
            st.session_state.messages.append({"role": "assistant", "content": content})
            salvar_chat(st.session_state.chat_atual, st.session_state.titulo_atual, st.session_state.messages)
        except Exception as e:
            st.error(f"Erro: {e}")
