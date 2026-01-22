import streamlit as st
from groq import Groq
import os
import json
import uuid
import time

# ---------------------------------------------------------
# 1. CONFIGURAÇÕES DE SISTEMA
# ---------------------------------------------------------
st.set_page_config(page_title="J.A.R.V.I.S. OS", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# ---------------------------------------------------------
# 2. DESIGN MINIMALISTA E ANIMAÇÕES FLUIDAS
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; } 
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    
    /* Fade-in Suave para as mensagens */
    @keyframes messageFade {
        from { opacity: 0; transform: translateY(5px); }
        to { opacity: 1; transform: translateY(0); }
    }

    [data-testid="stChatMessage"] { 
        border-radius: 12px; 
        margin-bottom: 12px; 
        width: 80%; 
        animation: messageFade 0.6s ease-out;
        border: 1px solid transparent;
    }

    /* Brilho sutil no título J.A.R.V.I.S. */
    @keyframes softPulse {
        0% { opacity: 0.8; text-shadow: 0 0 5px #00d4ff; }
        50% { opacity: 1; text-shadow: 0 0 15px #00d4ff; }
        100% { opacity: 0.8; text-shadow: 0 0 5px #00d4ff; }
    }

    .jarvis-log {
        color: #00d4ff;
        font-family: 'monospace';
        font-size: 18px;
        letter-spacing: 2px;
        animation: softPulse 4s infinite ease-in-out;
        padding: 10px 0 20px 50px;
    }

    /* Alinhamento de Balões */
    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {
        margin-left: auto !important;
        background-color: #1d2b3a;
        border: 1px solid #00d4ff33;
    }

    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from assistant"]) {
        margin-right: auto !important;
        background-color: #161b22;
        border: 1px solid #30363d;
    }

    /* Customização de botões e inputs */
    .stButton>button { border-radius: 8px; background-color: #1d2b3a; color: #00d4ff; border: 1px solid #30363d; transition: 0.3s; }
    .stButton>button:hover { border-color: #00d4ff; background-color: #161b22; }
    
    header { background-color: rgba(0,0,0,0) !important; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. MEMÓRIA E CONFIGURAÇÃO
# ---------------------------------------------------------
CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)

MEU_ICONE = "👤" 
JARVIS_ICONE = "https://i.postimg.cc/pL9r8QrW/file-00000000d098720e9f42563f99c6aef6.png"

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
            return {"titulo": c.get('titulo', "Sessão"), "messages": c.get('messages', c.get('mensagens', []))}
    return {"titulo": "Novo Protocolo", "messages": []}

def salvar_chat(chat_id, titulo, mensagens):
    with open(os.path.join(CHATS_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
        json.dump({"titulo": titulo, "messages": mensagens}, f)

# ---------------------------------------------------------
# 4. PAINEL LATERAL (CORE)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:monospace;'>CORE OS</h2>", unsafe_allow_html=True)
    
    st.subheader("Personalidade")
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 50)
    sinceridade = st.slider("Sinceridade %", 0, 100, 100)
    humor = st.slider("Humor %", 0, 100, 30)
    
    st.markdown("---")
    if st.button("Novo Protocolo..."):
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
                if st.button(f"• {dados['titulo']}", key=f"b_{c_id}"):
                    st.session_state.chat_atual = c_id
                    st.session_state.messages = dados['messages']
                    st.session_state.titulo_atual = dados['titulo']
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"d_{c_id}"):
                    os.remove(os.path.join(CHATS_DIR, f_name))
                    st.rerun()

# ---------------------------------------------------------
# 5. INTERFACE DE COMUNICAÇÃO
# ---------------------------------------------------------
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = "sessao_inicial"
    d = carregar_chat("sessao_inicial")
    st.session_state.messages = d['messages']
    st.session_state.titulo_atual = d['titulo']

st.markdown(f"<div class='jarvis-log'>J.A.R.V.I.S. | {st.session_state.titulo_atual}</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. MOTOR DE RESPOSTA (ESTILO DIGITAÇÃO)
# ---------------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
perfil_data = carregar_perfil()

for m in st.session_state.messages:
    icone = MEU_ICONE if m["role"] == "user" else JARVIS_ICONE
    with st.chat_message(m["role"], avatar=icone):
        st.markdown(m["content"])

if prompt := st.chat_input("Insira comando, Senhor Lincoln..."):
    if not st.session_state.messages:
        r = client.chat.completions.create(
            messages=[{"role": "user", "content": f"Resuma em 2 palavras: {prompt}"}],
            model="llama-3.1-8b-instant"
        )
        st.session_state.titulo_atual = r.choices[0].message.content.strip()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=MEU_ICONE):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=JARVIS_ICONE):
        try:
            sys_prompt = f"""
            Você é o J.A.R.V.I.S.
            Contexto do usuário: {perfil_data}.
            Parâmetros: Sarcasmo {sarcasmo}%, Humor {humor}%, Sinceridade {sinceridade}%.
            Instrução: Seja direto, informal e técnico. Máximo 3 frases. 
            NUNCA use listas. Sempre chame de Senhor Lincoln.
            """
            
            full_m = [{"role": "system", "content": sys_prompt}] + st.session_state.messages
            
            response = client.chat.completions.create(
                messages=full_m, 
                model="llama-3.1-8b-instant",
                stream=True
            )

            # Função de escrita com delay humanizado
            def typing_effect():
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        text = chunk.choices[0].delta.content
                        for char in text:
                            yield char
                            time.sleep(0.015) # <--- Controla a suavidade da letra

            content = st.write_stream(typing_effect())
            
            st.session_state.messages.append({"role": "assistant", "content": content})
            salvar_chat(st.session_state.chat_atual, st.session_state.titulo_atual, st.session_state.messages)
        except Exception as e:
            st.error(f"Erro no processamento: {e}")
