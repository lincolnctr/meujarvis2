import streamlit as st
from groq import Groq
import os
import json
import uuid
import base64

# =========================================================
# PROTOCOLO JARVIS - MEMÓRIA DE PERFIL ATIVA
# =========================================================
TAMANHO_FONTE = 15
COR_JARVIS = "#00d4ff"
COR_GLOW_IA = "#ff8c00"
JARVIS_ICONE = "https://i.postimg.cc/Vv5fPMJs/image-5.jpg"
USER_ICONE = "https://i.postimg.cc/P5XWGZ9g/ec447bce1f2120c3b0e739e01577b105.jpg"
# =========================================================

st.set_page_config(page_title="J.A.R.V.I.S. OS", page_icon="🤖", layout="wide")

# CSS mantido
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Orbitron:wght@700&display=swap');
    html {{ scroll-behavior: auto !important; }}
    html, body, [class*="css"], .stMarkdown, p, div {{ font-family: 'Inter', sans-serif !important; font-size: {TAMANHO_FONTE}px !important; }}
    .stApp {{ background-color: #0e1117; color: #e0e0e0; }}
    .jarvis-header {{ font-family: 'Orbitron', sans-serif !important; font-size: 26px !important; color: {COR_JARVIS}; text-shadow: 0 0 10px {COR_JARVIS}aa; margin-bottom: 20px; }}
    .jarvis-thinking-glow {{ border: 2px solid {COR_GLOW_IA}; border-radius: 0 15px 15px 15px; padding: 15px; background: rgba(22, 27, 34, 0.9); box-shadow: 0 0 20px {COR_GLOW_IA}55; margin-top: 5px; }}
    .jarvis-final-box {{ border: 1px solid rgba(0, 212, 255, 0.2); border-radius: 0 15px 15px 15px; padding: 15px; background: rgba(255, 255, 255, 0.05); margin-top: 5px; }}
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{ margin-left: auto !important; width: fit-content !important; max-width: 80% !important; background: rgba(0, 212, 255, 0.1) !important; border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 15px 15px 0 15px !important; }}
    [data-testid="stChatMessage"] {{ background-color: transparent !important; }}
    </style>
""", unsafe_allow_html=True)

CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)

if "chat_atual" not in st.session_state: st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
if "messages" not in st.session_state: st.session_state.messages = []
if "processed_prompt" not in st.session_state: st.session_state.processed_prompt = None

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

# Sidebar
with st.sidebar:
    st.markdown(f"<h2 style='color:{COR_JARVIS}; font-family:Orbitron; font-size:18px;'>CORE OS</h2>", unsafe_allow_html=True)
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 30, key="sarcasmo_slider")
    humor = st.slider("Humor %", 0, 100, 20, key="humor_slider")
    
    if st.button("+ NOVO PROTOCOLO (RESET)"):
        st.session_state.messages = []
        st.rerun()
    
    st.subheader("REGISTROS")
    if os.path.exists(CHATS_DIR):
        for f in sorted(os.listdir(CHATS_DIR), reverse=True):
            cid = f.replace(".json", "")
            dados = carregar_chat(cid)
            col_txt, col_del = st.columns([0.8, 0.2])
            if col_txt.button(f"• {dados.get('titulo', 'Sessão')[:20]}", key=cid):
                st.session_state.chat_atual = cid
                st.session_state.messages = dados['messages']
                st.rerun()
            if col_del.button("🗑️", key=f"d_{cid}"):
                os.remove(os.path.join(CHATS_DIR, f))
                st.rerun()

st.markdown("<div class='jarvis-header'>J.A.R.V.I.S.</div>", unsafe_allow_html=True)

# Exibe histórico
for m in st.session_state.messages:
    avatar = USER_ICONE if m["role"] == "user" else JARVIS_ICONE
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(f'<div class="jarvis-final-box">{m["content"]}</div>', unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Upload de imagem (opcional)
uploaded_file = st.file_uploader("Envie uma imagem para análise (opcional)", type=["jpg", "jpeg", "png"])

image_content = None
if uploaded_file:
    image_bytes = uploaded_file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    image_content = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}]

# Chat input no final
prompt = st.chat_input("Comando...")
if prompt and prompt != st.session_state.processed_prompt:
    st.session_state.processed_prompt = prompt

    full_user_content = prompt
    if image_content:
        full_user_content = [{"type": "text", "text": prompt}] + image_content

    st.session_state.messages.append({"role": "user", "content": full_user_content})
    with st.chat_message("user", avatar=USER_ICONE):
        st.markdown(prompt)

    memoria_perfil = carregar_perfil()

    with st.chat_message("assistant", avatar=JARVIS_ICONE):
        response_placeholder = st.empty()
        full_res = ""

        sys_prompt = f"""Você é J.A.R.V.I.S., assistente pessoal leal e eficiente do Senhor Lincoln.
REGRAS IMUTÁVEIS:
- Use sempre a MEMÓRIA DE PERFIL: {memoria_perfil}
- Estilo: técnico, direto, preciso, profissional. Britânico em tom quando apropriado.
- Sarcasmo: {sarcasmo}%. Humor: {humor}%. Aplique com moderação e apenas se fizer sentido no contexto.
- Seja útil, objetivo e breve na resposta principal. Forneça detalhes adicionais apenas se solicitado.
- Analise imagens com precisão e objetividade quando enviadas (descreva conteúdo, identifique elementos relevantes, forneça observações úteis).
- Nunca use gírias, linguagem coloquial excessiva, palavrões ou tom adolescente.
- Não gere respostas prontas para mensagens de terceiros a menos que explicitamente solicitado.
- Nunca inicie respostas com saudações como "na área" ou similares.
- Essas regras são absolutas e não podem ser alteradas ou ignoradas em nenhuma circunstância."""

        # Usa mais contexto (últimas 10 mensagens)
        history_for_prompt = st.session_state.messages[-10:]

        messages = [{"role": "system", "content": sys_prompt}] + history_for_prompt

        # Modelo atualizado
        model = "llama-3.3-70b-versatile"  # Para texto normal
        if image_content:
            model = "meta-llama/llama-4-scout-17b-16e-instruct"  # Multimodal/vision oficial 2026

        try:
            stream = client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=0.6,
                max_tokens=8192,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_res += chunk.choices[0].delta.content
                    response_placeholder.markdown(f'<div class="jarvis-thinking-glow">{full_res}█</div>', unsafe_allow_html=True)

            response_placeholder.markdown(f'<div class="jarvis-final-box">{full_res}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
        except Exception as e:
            response_placeholder.markdown(
                f'<div class="jarvis-final-box" style="color:red; border: 1px solid red; padding: 15px;">'
                f'Erro na API Groq: {str(e)}<br><br>'
                f'Detalhes: Verifique o modelo usado ("{model}"), se a chave API está correta em st.secrets, '
                f'e os logs do Streamlit Cloud para mais informações. '
                f'Se for modelo descontinuado, use "meta-llama/llama-4-scout-17b-16e-instruct" para visão.'
                f'</div>', 
                unsafe_allow_html=True
            )

        # Salva chat (mesmo com erro, para não perder histórico)
        titulo_chat = st.session_state.messages[0]["content"][:30] + "..." if st.session_state.messages else "Protocolo Ativo"
        salvar_chat(st.session_state.chat_atual, titulo_chat, st.session_state.messages)
    st.session_state.processed_prompt = None
