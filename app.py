import streamlit as st
from groq import Groq
import os
import json
import uuid

# =========================================================
# PAINEL DE CONFIGURAÇÃO MANUAL
# =========================================================
TAMANHO_FONTE = 14          
COR_JARVIS = "#00d4ff"      
DISTANCIA_LINHAS = 1.5      
# =========================================================

st.set_page_config(page_title="J.A.R.V.I.S. OS", page_icon="🤖", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Orbitron:wght@700&display=swap');
    
    html, body, [class*="css"], .stMarkdown, p, div {{ 
        font-family: 'Inter', sans-serif !important; 
        font-size: {TAMANHO_FONTE}px !important; 
        line-height: {DISTANCIA_LINHAS} !important;
    }}
    
    .stApp {{ background-color: #0e1117; color: #e0e0e0; }}
    
    .jarvis-header {{ 
        font-family: 'Orbitron', sans-serif !important; 
        font-size: 28px !important; 
        font-weight: 700; color: {COR_JARVIS}; 
        letter-spacing: 3px; text-shadow: 0 0 10px {COR_JARVIS}aa; 
        margin-bottom: 15px; 
    }}
    
    /* Alinhamento das Mensagens */
    [data-testid="stChatMessage"] {{
        background-color: transparent !important;
    }}
    
    /* Mensagem do Usuário (Direita) */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
        flex-direction: row-reverse !important;
        text-align: right !important;
    }}
    
    /* Balão de resposta do JARVIS (Esquerda) */
    .jarvis-active-border {{ 
        border: 1px solid rgba(255, 140, 0, 0.4); 
        border-radius: 8px; padding: 12px 18px; 
        background: rgba(22, 27, 34, 0.6); margin-top: 5px; 
        text-align: left !important;
    }}

    /* Ajuste fino dos botões na Sidebar */
    .sidebar-btn-container {{
        display: flex;
        align-items: center;
        gap: 5px;
        margin-bottom: 5px;
    }}
    </style>
""", unsafe_allow_html=True)

CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)
JARVIS_ICONE = "https://i.postimg.cc/pL9r8QrW/file-00000000d098720e9f42563f99c6aef6.png"

if "chat_atual" not in st.session_state: st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
if "messages" not in st.session_state: st.session_state.messages = []
if "titulo_atual" not in st.session_state: st.session_state.titulo_atual = "SESSÃO INICIAL"

def carregar_chat(chat_id):
    path = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    return {"titulo": "Novo Registro", "messages": []}

def salvar_chat(chat_id, titulo, msgs):
    with open(os.path.join(CHATS_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
        json.dump({"titulo": titulo, "messages": msgs}, f)

# ---------------------------------------------------------
# SIDEBAR COM LIXEIRA LATERAL
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(f"<h2 style='color:{COR_JARVIS}; font-family:Orbitron; font-size:18px;'>CORE OS</h2>", unsafe_allow_html=True)
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 45)
    humor = st.slider("Humor %", 0, 100, 40)
    sinceridade = st.slider("Sinceridade %", 0, 100, 85)
    
    st.markdown("---")
    if st.checkbox("LOG DE MODIFICAÇÕES", value=True):
        st.info("Layout espelhado: Usuário na Direita.")
        st.success("Lixeira alinhada lateralmente.")
    
    if st.button("+ NOVO PROTOCOLO", use_container_width=True):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"; st.session_state.messages = []; st.session_state.titulo_atual = "NOVA SESSÃO"; st.rerun()

    st.subheader("REGISTROS")
    if os.path.exists(CHATS_DIR):
        for f in sorted(os.listdir(CHATS_DIR), reverse=True):
            cid = f.replace(".json", ""); dados = carregar_chat(cid)
            # COLUNAS PARA LIXEIRA LATERAL
            col_txt, col_del = st.columns([0.8, 0.2])
            with col_txt:
                if st.button(f"• {dados.get('titulo', 'Sessão')[:18]}", key=f"b_{cid}"):
                    st.session_state.chat_atual, st.session_state.messages = cid, dados['messages']
                    st.session_state.titulo_atual = dados.get('titulo', 'Sessão'); st.rerun()
            with col_del:
                if st.button("🗑️", key=f"d_{cid}"):
                    os.remove(os.path.join(CHATS_DIR, f)); st.rerun()

# ---------------------------------------------------------
# PROCESSAMENTO PRINCIPAL
# ---------------------------------------------------------
st.markdown("<div class='jarvis-header'>J.A.R.V.I.S.</div>", unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar=(None if m["role"]=="user" else JARVIS_ICONE)):
        st.markdown(m["content"])

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Comando, Senhor Lincoln..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant", avatar=JARVIS_ICONE):
        response_placeholder = st.empty(); full_res = ""
        
        if len(st.session_state.messages) <= 2:
            try:
                t_res = client.chat.completions.create(
                    messages=[{"role": "system", "content": "Resuma o tema em 2 palavras."}, {"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant"
                )
                st.session_state.titulo_atual = t_res.choices[0].message.content.strip().replace('"', '').upper()
            except: st.session_state.titulo_atual = "NOVA SESSÃO"

        sys_msg = (
            f"Você é o J.A.R.V.I.S., assistente britânico leal. Polido. "
            f"Sarcasmo {sarcasmo}%, Humor {humor}%, Sinceridade {sinceridade}%."
        )

        stream = client.chat.completions.create(
            messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages[-4:],
            model="llama-3.1-8b-instant", stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_res += chunk.choices[0].delta.content
                response_placeholder.markdown(f'<div class="jarvis-active-border">{full_res}█</div>', unsafe_allow_html=True)
        
        response_placeholder.markdown(full_res)
        st.session_state.messages.append({"role": "assistant", "content": full_res})
        salvar_chat(st.session_state.chat_atual, st.session_state.titulo_atual, st.session_state.messages)
