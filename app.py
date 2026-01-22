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
# 2. DESIGN: LINHA LARANJA MULTI-TOM (ESTILO HUD AVANÇADO)
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    
    /* Linha de Processamento Fixada ACIMA do Input */
    .stChatFloatingInputContainer {
        padding-top: 10px; /* Cria espaço para a linha no topo da barra de input */
    }

    .jarvis-orb-line {
        position: fixed;
        bottom: 90px; /* Posicionada exatamente acima da borda do chat_input */
        left: 0;
        width: 100%;
        height: 4px;
        z-index: 999999;
        background: transparent;
        transition: 0.5s;
    }

    /* Animação de Fluxo de Energia */
    @keyframes orange-flow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Estado Ativo: Gradiente com tons de Laranja (Claro, Médio e Escuro) */
    .active-energy {
        /* Paleta: Laranja Escuro (#CC4400), Médio (#FF8800), Claro (#FFBB33) */
        background: linear-gradient(90deg, #CC4400, #FF8800, #FFBB33, #FF8800, #CC4400);
        background-size: 200% 200%;
        animation: orange-flow 1.5s linear infinite;
        box-shadow: 0 -5px 15px rgba(255, 136, 0, 0.4);
    }

    /* Estado Idle: Linha sutil/apagada */
    .idle-energy {
        background: rgba(255, 136, 0, 0.05);
        height: 1px;
    }

    /* Estilo das Mensagens */
    [data-testid="stChatMessage"] { 
        border-radius: 12px; 
        width: 95% !important; 
        background-color: #161b22;
        border: 1px solid #30363d;
        margin-bottom: 10px;
    }

    .main .block-container { padding-bottom: 150px; }
    .jarvis-log { color: #00d4ff; font-family: 'monospace'; font-size: 18px; text-shadow: 0 0 10px #00d4ff55; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. COMPONENTE DE ENERGIA LARANJA
# ---------------------------------------------------------
def render_energy_line(active=False):
    status = "active-energy" if active else "idle-energy"
    return f'<div class="jarvis-orb-line {status}"></div>'

# ---------------------------------------------------------
# 4. FUNÇÕES DE MEMÓRIA
# ---------------------------------------------------------
CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)
MEU_ICONE = "👤" 
JARVIS_ICONE = "https://i.postimg.cc/pL9r8QrW/file-00000000d098720e9f42563f99c6aef6.png"

def carregar_chat(chat_id):
    caminho = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            c = json.load(f)
            return {"titulo": c.get('titulo', "Sessão"), "messages": c.get('messages', [])}
    return {"titulo": "Novo Protocolo", "messages": []}

def salvar_chat(chat_id, titulo, mensagens):
    with open(os.path.join(CHATS_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
        json.dump({"titulo": titulo, "messages": mensagens}, f)

# ---------------------------------------------------------
# 5. SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff; font-family:monospace;'>CORE OS</h2>", unsafe_allow_html=True)
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 50)
    
    if st.button("Novo Protocolo"):
        st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
        st.session_state.messages = []
        st.session_state.titulo_atual = "Aguardando..."
        st.rerun()

    st.subheader("Registros")
    if os.path.exists(CHATS_DIR):
        for f_name in sorted(os.listdir(CHATS_DIR), reverse=True):
            c_id = f_name.replace(".json", "")
            dados = carregar_chat(c_id)
            if st.button(f"• {dados['titulo']}", key=f"btn_{c_id}"):
                st.session_state.chat_atual = c_id
                st.session_state.messages = dados['messages']
                st.session_state.titulo_atual = dados['titulo']
                st.rerun()

# ---------------------------------------------------------
# 6. INTERFACE DE CHAT
# ---------------------------------------------------------
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = "sessao_inicial"
    d = carregar_chat("sessao_inicial")
    st.session_state.messages, st.session_state.titulo_atual = d['messages'], d['titulo']

st.markdown(f"<div class='jarvis-log'>J.A.R.V.I.S. | {st.session_state.titulo_atual}</div>", unsafe_allow_html=True)

# Renderização das Mensagens
for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar=(MEU_ICONE if m["role"] == "user" else JARVIS_ICONE)):
        st.markdown(m["content"])

# Placeholder da Linha de Energia (Renderizada DEPOIS do histórico para ficar sobreposta)
energy_placeholder = st.empty()

# ---------------------------------------------------------
# 7. MOTOR REATIVO COM LUZES LARANJAS
# ---------------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Pergunte o que quiser..."):
    # Garante que a linha apareça no estado inicial
    energy_placeholder.markdown(render_energy_line(active=False), unsafe_allow_html=True)
    
    if not st.session_state.messages:
        r = client.chat.completions.create(messages=[{"role": "user", "content": f"Resuma em 2 palavras: {prompt}"}], model="llama-3.1-8b-instant")
        st.session_state.titulo_atual = r.choices[0].message.content.strip()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=MEU_ICONE):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=JARVIS_ICONE):
        # LIGA AS LUZES LARANJAS NO TOPO DA CAIXA
        energy_placeholder.markdown(render_energy_line(active=True), unsafe_allow_html=True)
        
        try:
            sys_msg = f"Você é o J.A.R.V.I.S. Chame de Senhor Lincoln. Sarcasmo {sarcasmo}%."
            history = [{"role": "system", "content": sys_msg}] + st.session_state.messages
            response = client.chat.completions.create(messages=history, model="llama-3.1-8b-instant", stream=True)

            def fluidez():
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                        time.sleep(0.01)

            full_res = st.write_stream(fluidez())
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            salvar_chat(st.session_state.chat_atual, st.session_state.titulo_atual, st.session_state.messages)
            
        finally:
            # DESLIGA A ANIMAÇÃO (Retorna ao estado idle)
            energy_placeholder.markdown(render_energy_line(active=False), unsafe_allow_html=True)
else:
    # Mantém a linha visível em standby acima do input
    energy_placeholder.markdown(render_energy_line(active=False), unsafe_allow_html=True)
