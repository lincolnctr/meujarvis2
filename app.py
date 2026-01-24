import streamlit as st
from groq import Groq
import os
import json
import uuid
import base64
import random

# =========================================================
# PROTOCOLO JARVIS - MEMÓRIA DE PERFIL ATIVA
# =========================================================
TAMANHO_FONTE = 15
COR_JARVIS = "#00d4ff" 
COR_GLOW_IA = "#ff8c00"
JARVIS_ICONE = "https://i.postimg.cc/Vv5fPMJs/image-5.jpg"
USER_ICONE = "https://i.postimg.cc/4dSh6gqX/2066977d987392ae818f017008a2a7d6.jpg"
# =========================================================

# =========================================================
# CONFIGURAÇÃO DE CORES DA BARRA DESLIZANTE (PERSONALIZE AQUI)
# =========================================================
COR_BARRA_1 = "#ff8c00"  
COR_BARRA_2 = "#ffa500"  
COR_BARRA_3 = "#ff4500"  
# =========================================================

st.set_page_config(page_title="J.A.R.V.I.S. OS", page_icon="🤖", layout="wide")


st.markdown(f"""
    <style>
    :root {{
        /* ########## VARIAVEIS CSS PARA PERSONALIZAR ########## */
        --cor-barra-inicio: {COR_BARRA_1}; 
        --cor-barra-meio: {COR_BARRA_2};
        --cor-barra-fim: {COR_BARRA_3};
        /* ##################################################### */
    }}

    @import url('https://fonts.googleapis.com');

    html {{ scroll-behavior: smooth !important; }}
    .stApp {{ background-color: #0e1117; color: #e0e0e0; padding-bottom: 120px; }}

    .jarvis-header {{ 
        font-family: 'orbitron', sans-serif !important; 
        font-size: 26px !important; 
        color: var(--cor-jarvis-brilho); 
        text-align: center; 
        animation: jarvis-pulse 3s infinite alternate ease-in-out;
    }}

    @keyframes jarvis-pulse {{
        0% {{ text-shadow: 0 0 5px var(--cor-jarvis-brilho)aa, 0 0 15px var(--cor-jarvis-brilho)77; }}
        100% {{ text-shadow: 0 0 15px var(--cor-jarvis-brilho), 0 0 40px var(--cor-jarvis-brilho)99; }}
    }}

    .jarvis-thinking-glow {{ 
        border: 2px solid {COR_GLOW_IA}; 
        border-radius: 0 25px 25px 25px; 
        padding: 15px; 
        background: rgba(22, 27, 34, 0.9); 
        box-shadow: 0 0 20px {COR_GLOW_IA}55; 
        margin-top: 5px;
        max-width: var(--largura-maxima-msgs) !important; /* Expansão J.A.R.V.I.S. */
    }}

    .jarvis-final-box {{ 
        border: 1px solid rgba(0, 212, 255, 0.05); 
        border-radius: 0 15px 15px 15px; 
        padding: 15px; 
        background: rgba(255, 255, 255, 0.05); 
        margin-top: 5px;
        max-width: var(--largura-maxima-msgs) !important; /* Expansão J.A.R.V.I.S. */
    }}

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{ 
        margin-left: auto !important; 
        width: fit-content !important; 
        max-width: var(--largura-maxima-msgs) !important; /* Expansão Lincoln */
        background: rgba(0, 212, 255, 0.1) !important; 
        border: 1px solid rgba(0, 212, 255, 0.3); 
        border-radius: 15px 15px 0 15px !important; 
    }}

    [data-testid="stChatMessage"] {{ background-color: transparent !important; }}

    .stApp:has([data-testid="stChatInput"] textarea:focus) {{
        background: radial-gradient(circle at bottom, var(--cor-barra-inicio)11 0%, #05070a 100%) !important;
        transition: background 0.5s ease;
    }}

    [data-testid="stChatInput"] {{
        position: fixed !important;
        bottom: 0px !important; 
        width: 100vw !important; 
        left: 0px !important; 
        z-index: 1000 !important;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        padding: 10px 0px 30px 0px !important; 
        background: #0e1117; 
    }}

    [data-testid="stChatInput"] textarea {{
        background: rgba(22, 27, 34, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 12px !important;
        width: 100% !important; 
    }}
    </style>
""", unsafe_allow_html=True)

# ... [O restante do código permanece idêntico ao enviado por você] ...

CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)

if "chat_atual" not in st.session_state: st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
if "messages" not in st.session_state: st.session_state.messages = []
if "processed_prompt" not in st.session_state: st.session_state.processed_prompt = None
if "log_modificacoes" not in st.session_state: st.session_state.log_modificacoes = []
if "humor_nivel" not in st.session_state: st.session_state.humor_nivel = 59
if "sinceridade_nivel" not in st.session_state: st.session_state.sinceridade_nivel = 75
if "is_thinking" not in st.session_state: st.session_state.is_thinking = False

def carregar_perfil():
    if os.path.exists("perfil.txt"):
        with open("perfil.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    return "Nenhuma informação de perfil encontrada."

def carregar_chat(chat_id):
    path = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    return {"titulo": "Novo Protocolo", "messages": []}

def salvar_chat(chat_id, titulo, msgs):
    with open(os.path.join(CHATS_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
        json.dump({"titulo": titulo, "messages": msgs}, f)

with st.sidebar:
    st.markdown(f"<h2 style='color:{COR_JARVIS}; font-family:Orbitron; font-size:18px;'>CORE OS</h2>", unsafe_allow_html=True)
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 52, key="sarcasmo_slider")
    humor = st.slider("Humor %", 0, 100, st.session_state.humor_nivel, key="humor_slider")
    st.session_state.humor_nivel = humor
    sinceridade = st.slider("Sinceridade %", 0, 100, st.session_state.sinceridade_nivel, key="sinceridade_slider")
    st.session_state.sinceridade_nivel = sinceridade

    if st.button("+ NOVO PROTOCOLO (RESET)"):
        st.session_state.messages = []
        st.rerun()

    st.subheader("REGISTROS")
    if os.path.exists(CHATS_DIR):
        for f in sorted(os.listdir(CHATS_DIR), reverse=True):
            cid = f.replace(".json", "")
            dados = carregar_chat(cid)
            col_txt, col_del, col_rename = st.columns([0.6, 0.2, 0.2])
            if col_txt.button(f"• {dados.get('titulo', 'Sessão')[:20]}", key=cid):
                st.session_state.chat_atual = cid
                st.session_state.messages = dados['messages']
                st.rerun()
            if col_del.button("×", key=f"d_{cid}"):
                os.remove(os.path.join(CHATS_DIR, f))
                st.rerun()
            with col_rename:
                if st.button("📝", key=f"r_{cid}"):
                    novo_titulo = st.text_input("Novo título:", value=dados.get('titulo', 'Sessão'), key=f"n_{cid}")
                    if st.button("Salvar", key=f"s_{cid}"):
                        salvar_chat(cid, novo_titulo, dados['messages'])
                        st.rerun()

st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True) 
st.markdown("<p class='jarvis-header'>J.A.R.V.I.S.</p>", unsafe_allow_html=True)

for m in st.session_state.messages:
    avatar = USER_ICONE if m["role"] == "user" else JARVIS_ICONE
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(f'<div class="jarvis-final-box">{m["content"]}</div>', unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Comando..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_ICONE):
        st.markdown(prompt)

    memoria_perfil = carregar_perfil()
    
    with st.chat_message("assistant", avatar=JARVIS_ICONE):
        response_placeholder = st.empty()
        full_res = ""
        sys_prompt = f"Você é J.A.R.V.I.S., assistente leal do Senhor Lincoln. Perfil: {memoria_perfil}. Humor: {humor}%. Sarcasmo: {sarcasmo}%. Sinceridade: {sinceridade}%."

        stream = client.chat.completions.create(
            messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages[-10:],
            model="llama-3.3-70b-versatile", stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_res += chunk.choices[0].delta.content
                response_placeholder.markdown(f'<div class="jarvis-thinking-glow">{full_res}█</div>', unsafe_allow_html=True)

        response_placeholder.markdown(f'<div class="jarvis-final-box">{full_res}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": full_res})
        salvar_chat(st.session_state.chat_atual, "PROTOCOLO ATIVO", st.session_state.messages)

        if st.session_state.humor_nivel > 30 and random.random() < 0.2:
            humor_respostas = ["Espero que isso tenha ajudado!", "Era isso! O que mais posso ajudar?"]
            st.markdown(f'<div class="jarvis-final-box">{random.choice(humor_respostas)}</div>', unsafe_allow_html=True)
