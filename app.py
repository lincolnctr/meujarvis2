import streamlit as st
from groq import Groq
import os
import json
import uuid
import time

# ---------------------------------------------------------
# 1. INTERFACE HUD (ESTILO LIMPO E ESCALADO)
# ---------------------------------------------------------
st.set_page_config(page_title="J.A.R.V.I.S. OS", page_icon="🤖", layout="wide")

# CSS Ajustado para Fontes Similares ao Chat Atual e Escala Menor
st.markdown("""
    <style>
    /* Importando fonte limpa */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Orbitron:wght@700&display=swap');
    
    /* Redução de Zoom e Troca de Fonte */
    html, body, [class*="css"], .stMarkdown, p, div { 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; 
        font-size: 14px !important; /* Diminuído para remover aspecto de zoom */
        line-height: 1.5 !important;
    }
    
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    
    /* Título J.A.R.V.I.S menor */
    .jarvis-header { 
        font-family: 'Orbitron', sans-serif !important; 
        font-size: 28px !important; 
        font-weight: 700; 
        color: #00d4ff; 
        letter-spacing: 3px; 
        text-shadow: 0 0 10px #00d4ffaa; 
        margin-bottom: 5px; 
    }
    
    /* Balão de resposta mais elegante e compacto */
    .jarvis-active-border { 
        border: 1px solid rgba(255, 140, 0, 0.4); 
        border-radius: 8px; 
        padding: 12px 18px; 
        background: rgba(22, 27, 34, 0.6); 
        margin-top: 5px; 
    }

    /* Ajuste de largura do input */
    .stChatInput { padding-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

# O SCRIPT DE AUTO-SCROLL FOI REMOVIDO POR SOLICITAÇÃO

# ---------------------------------------------------------
# 2. SISTEMA DE MEMÓRIA E PROTOCOLO DE LEITURA
# ---------------------------------------------------------
CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)
JARVIS_ICONE = "https://i.postimg.cc/pL9r8QrW/file-00000000d098720e9f42563f99c6aef6.png"

def obter_essencia_do_codigo():
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            return "".join([l for l in f.readlines() if "st.markdown" not in l])
    except: return "Protocolo de leitura falhou."

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
# 3. CORE OS: BARRA LATERAL (SIDEBAR)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:Orbitron; font-size:18px;'>CORE OS</h2>", unsafe_allow_html=True)
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 45)
    humor = st.slider("Humor %", 0, 100, 40)
    sinceridade = st.slider("Sinceridade %", 0, 100, 85)
    
    st.markdown("---")
    if st.checkbox("LOG DE MODIFICAÇÕES"):
        st.info("Interface otimizada: Fonte 'Inter' aplicada e Scroll automático desativado.")
    
    if st.button("+ NOVO PROTOCOLO"):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"; st.session_state.messages = []; st.session_state.titulo_atual = "AGUARDANDO..."; st.rerun()

    st.subheader("REGISTROS")
    if os.path.exists(CHATS_DIR):
        for f in sorted(os.listdir(CHATS_DIR), reverse=True):
            cid = f.replace(".json", ""); dados = carregar_chat(cid)
            col1, col2 = st.columns([0.8, 0.2])
            if col1.button(f"• {dados.get('titulo', 'Sessão')}", key=f"b_{cid}"):
                st.session_state.chat_atual, st.session_state.messages = cid, dados['messages']
                st.session_state.titulo_atual = dados.get('titulo', 'Sessão'); st.rerun()
            if col2.button("🗑️", key=f"d_{cid}"): os.remove(os.path.join(CHATS_DIR, f)); st.rerun()

# ---------------------------------------------------------
# 4. PROCESSAMENTO E PERSONALIDADE
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
        response_placeholder = st.empty()
        full_res = ""
        
        contexto = ""
        if any(word in prompt.lower() for word in ["código", "script", "atualize", "mude"]):
            contexto = f"\n\nLÓGICA ATUAL:\n{obter_essencia_do_codigo()}"

        sys_msg = (
            f"Você é o J.A.R.V.I.S., assistente britânico sofisticado do Senhor Lincoln. "
            f"Fale com polidez e eficiência. Evite textos longos ou poéticos. "
            f"Se solicitado código, forneça o script completo de forma organizada. "
            f"Sarcasmo {sarcasmo}%, Humor {humor}%, Sinceridade {sinceridade}%."
            f"{contexto}"
        )

        try:
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
        except Exception as e: st.error(f"Erro no Core: {e}")
