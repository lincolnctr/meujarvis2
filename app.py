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
# 2. DESIGN, HOLOGRAMA E ANIMAÇÕES
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; } 
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    
    /* Animações do Holograma */
    @keyframes spinHologram { 100% { transform: rotate(360deg); } }
    @keyframes pulseGlow {
        0%, 100% { filter: drop-shadow(0 0 5px #00d4ff) brightness(1); opacity: 0.8; }
        50% { filter: drop-shadow(0 0 25px #00c4ff) brightness(1.3); opacity: 1; }
    }

    /* Classe do Holograma Ativo */
    .hologram-active {
        width: 180px;
        border-radius: 50%;
        animation: spinHologram 15s linear infinite, pulseGlow 2s infinite ease-in-out;
        display: block;
        margin: 20px auto;
    }

    /* Classe do Holograma em Espera (Apagado) */
    .hologram-idle {
        width: 140px;
        border-radius: 50%;
        filter: grayscale(100%);
        opacity: 0.2;
        display: block;
        margin: 20px auto;
        transition: 1s;
    }

    /* Estilização dos Balões de Chat Expandidos */
    [data-testid="stChatMessage"] { 
        border-radius: 12px; 
        margin-bottom: 15px; 
        width: 95% !important; 
        max-width: 100% !important; 
        animation: fadeIn 0.7s ease-out;
    }

    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    .jarvis-log {
        color: #00d4ff;
        font-family: 'monospace';
        font-size: 18px;
        padding: 15px 0 15px 50px;
        letter-spacing: 2px;
        text-shadow: 0 0 10px #00d4ff55;
    }

    /* Alinhamento dos Balões */
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

    header { background-color: rgba(0,0,0,0) !important; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. MEMÓRIA E CONFIGURAÇÕES DE IMAGEM
# ---------------------------------------------------------
CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)

MEU_ICONE = "👤" 
JARVIS_ICONE = "https://i.postimg.cc/pL9r8QrW/file-00000000d098720e9f42563f99c6aef6.png"
HOLOG_IMG = "https://i.postimg.cc/Vv5fPMJs/image-5.jpg"

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
# 4. PAINEL LATERAL COM HOLOGRAMA REATIVO
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:monospace;'>CORE OS</h2>", unsafe_allow_html=True)
    
    # Placeholder para o Holograma (ele muda de classe via script)
    hologram_spot = st.empty()
    hologram_spot.markdown(f'<img src="{HOLOG_IMG}" class="hologram-idle">', unsafe_allow_html=True)
    
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
            if st.button(f"• {dados['titulo']}", key=f"b_{c_id}"):
                st.session_state.chat_atual = c_id
                st.session_state.messages = dados['messages']
                st.session_state.titulo_atual = dados['titulo']
                st.rerun()

# ---------------------------------------------------------
# 5. TELA DE CHAT
# ---------------------------------------------------------
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = "sessao_inicial"
    d = carregar_chat("sessao_inicial")
    st.session_state.messages = d['messages']
    st.session_state.titulo_atual = d['titulo']

st.markdown(f"<div class='jarvis-log'>J.A.R.V.I.S. | {st.session_state.titulo_atual}</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. MOTOR COM HOLOGRAMA ATIVO
# ---------------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
perfil_data = carregar_perfil()

for m in st.session_state.messages:
    icone = MEU_ICONE if m["role"] == "user" else JARVIS_ICONE
    with st.chat_message(m["role"], avatar=icone):
        st.markdown(m["content"])

if prompt := st.chat_input("Comando..."):
    # Salvar e mostrar mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=MEU_ICONE):
        st.markdown(prompt)

    # Resposta do JARVIS
    with st.chat_message("assistant", avatar=JARVIS_ICONE):
        # LIGA O HOLOGRAMA (Ativa animação e luz)
        hologram_spot.markdown(f'<img src="{HOLOG_IMG}" class="hologram-active">', unsafe_allow_html=True)
        
        try:
            sys_prompt = f"Você é o J.A.R.V.I.S., IA de {perfil_data}. Chame de Senhor Lincoln. Seja direto. Sarcasmo {sarcasmo}%."
            full_m = [{"role": "system", "content": sys_prompt}] + st.session_state.messages
            
            response = client.chat.completions.create(messages=full_m, model="llama-3.1-8b-instant", stream=True)

            def stream_typing():
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                        time.sleep(0.01)

            # Efeito de escrita enquanto o holograma brilha
            content = st.write_stream(stream_typing())
            
            st.session_state.messages.append({"role": "assistant", "content": content})
            salvar_chat(st.session_state.chat_atual, st.session_state.titulo_atual, st.session_state.messages)
            
        finally:
            # DESLIGA O HOLOGRAMA (Volta ao estado de repouso)
            hologram_spot.markdown(f'<img src="{HOLOG_IMG}" class="hologram-idle">', unsafe_allow_html=True)
