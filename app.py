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

# CSS atualizado com menu fixo e animação da esfera
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Orbitron:wght@700&display=swap');

    html {{ scroll-behavior: auto !important; }}
    html, body, [class*="css"], .stMarkdown, p, div {{ font-family: 'Inter', sans-serif !important; font-size: {TAMANHO_FONTE}px !important; }}
    .stApp {{ background-color: #0e1117; color: #e0e0e0; }}

    /* Menu fixo no topo */
    .top-menu {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: rgba(14, 17, 23, 0.9);
        backdrop-filter: blur(10px);
        padding: 10px 20px;
        z-index: 999;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid rgba(0, 212, 255, 0.2);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }}
    .jarvis-title {{
        font-family: 'Orbitron', sans-serif !important;
        font-size: 28px !important;
        color: {COR_JARVIS};
        text-shadow: 0 0 15px {COR_JARVIS}aa;
        margin: 0;
    }}

    /* Container da esfera + pensamentos */
    .thought-container {{
        display: flex;
        align-items: center;
        gap: 15px;
    }}
    .thought-sphere {{
        width: 80px;
        height: 80px;
        background-image: 'https://i.postimg.cc/Vv5fPMJs/image-5.jpg');  /* SUBSTITUA PELA SUA IMAGEM */
        background-size: cover;
        border-radius: 50%;
        box-shadow: 0 0 20px {COR_GLOW_IA}88;
        transition: all 0.5s ease;
    }}
    .thought-sphere.thinking {{
        animation: rotate 8s linear infinite, pulse 2s ease-in-out infinite;
    }}
    .thought-sphere.paused {{
        filter: grayscale(100%);
        box-shadow: 0 0 10px #555;
    }}
    @keyframes rotate {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    @keyframes pulse {{
        0% {{ box-shadow: 0 0 20px {COR_GLOW_IA}88; }}
        50% {{ box-shadow: 0 0 40px {COR_GLOW_IA}ff; }}
        100% {{ box-shadow: 0 0 20px {COR_GLOW_IA}88; }}
    }}

    /* Lista de pensamentos */
    .thought-list {{
        display: flex;
        flex-direction: column;
        gap: 8px;
        max-width: 250px;
    }}
    .thought-item {{
        background: rgba(255, 140, 0, 0.15);
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 14px;
        color: #ff8c00;
        border: 1px solid rgba(255, 140, 0, 0.3);
    }}
    .thought-item.thinking {{
        animation: fadePulse 1.5s infinite;
    }}
    @keyframes fadePulse {{
        0%, 100% {{ opacity: 0.6; }}
        50% {{ opacity: 1; }}
    }}

    /* Ajustes no resto da página */
    .stApp > div:first-child {{ margin-top: 100px !important; }}  /* Espaço para menu fixo */
    </style>
""", unsafe_allow_html=True)

CHATS_DIR = "chats_db"
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)

if "chat_atual" not in st.session_state: st.session_state.chat_atual = f"chat_{uuid.uuid4().hex[:6]}"
if "messages" not in st.session_state: st.session_state.messages = []
if "processed_prompt" not in st.session_state: st.session_state.processed_prompt = None
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

# Menu fixo no topo com esfera e pensamentos
st.markdown("""
    <div class="top-menu">
        <h1 class="jarvis-title">J.A.R.V.I.S.</h1>
        <div class="thought-container">
            <div id="thought-sphere" class="thought-sphere paused"></div>
            <div class="thought-list">
                <div class="thought-item">Pensamento 1: Estilo detectado</div>
                <div class="thought-item">Pensamento 2: Objetivo acumulado</div>
                <!-- Mais itens serão adicionados dinamicamente depois -->
            </div>
        </div>
    </div>

    <script>
        const sphere = document.getElementById('thought-sphere');
        // Detecta se está pensando (pode ser ajustado via Streamlit callback depois)
        function updateThinking(state) {
            if (state === 'thinking') {
                sphere.classList.add('thinking');
                sphere.classList.remove('paused');
            } else {
                sphere.classList.remove('thinking');
                sphere.classList.add('paused');
            }
        }
        // Por enquanto, ativa ao carregar (teste)
        updateThinking('thinking');
        setTimeout(() => updateThinking('paused'), 5000);
    </script>
""", unsafe_allow_html=True)

# Exibe histórico (com margem para o menu fixo)
st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)  # Espaço extra

for m in st.session_state.messages:
    avatar = USER_ICONE if m["role"] == "user" else JARVIS_ICONE
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(f'<div class="jarvis-final-box">{m["content"]}</div>', unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Chat input
prompt_obj = st.chat_input(
    "Comando...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
    max_upload_size=10,
    key="jarvis_chat_input"
)

if prompt_obj and prompt_obj != st.session_state.processed_prompt:
    st.session_state.processed_prompt = prompt_obj
    st.session_state.is_thinking = True  # Ativa modo pensamento

    user_text = prompt_obj.text.strip() if hasattr(prompt_obj, 'text') and prompt_obj.text else ""
    uploaded_files = prompt_obj.files if hasattr(prompt_obj, 'files') else []

    if user_text or uploaded_files:
        image_content = None

        if uploaded_files:
            file = uploaded_files[0]
            image_bytes = file.read()
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            image_content = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}]

            with st.chat_message("user", avatar=USER_ICONE):
                st.image(file, caption="Imagem enviada", use_column_width=True)
                if user_text:
                    st.markdown(user_text)

        else:
            with st.chat_message("user", avatar=USER_ICONE):
                st.markdown(user_text)

        full_user_content = user_text
        if image_content:
            full_user_content = [{"type": "text", "text": user_text}] + image_content

        st.session_state.messages.append({"role": "user", "content": full_user_content})

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

            # Processamento normal
            history_for_prompt = st.session_state.messages[-10:]

            messages = [{"role": "system", "content": sys_prompt}] + history_for_prompt

            model = "llama-3.3-70b-versatile"
            if image_content:
                model = "meta-llama/llama-4-scout-17b-16e-instruct"

            try:
                stream = client.chat.completions.create(
                    messages=messages,
                    model=model,
                    temperature=0.6,
                    max_tokens=4096,
                    stream=True,
                    timeout=120
                )

                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta.content is not None:
                        full_res += delta.content
                        response_placeholder.markdown(f'<div class="jarvis-thinking-glow">{full_res}█</div>', unsafe_allow_html=True)

                response_placeholder.markdown(f'<div class="jarvis-final-box">{full_res}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": full_res})

            except groq.APIStatusError as e:
                response_placeholder.markdown(f'<div class="jarvis-final-box" style="color:red; border: 1px solid red; padding: 15px;">Erro de status na API Groq ({e.status_code}): {str(e)}</div>', unsafe_allow_html=True)
            except groq.APIConnectionError as e:
                response_placeholder.markdown(f'<div class="jarvis-final-box" style="color:orange; border: 1px solid orange; padding: 15px;">Erro de conexão/timeout na Groq: {str(e)}</div>', unsafe_allow_html=True)
            except groq.APIError as e:
                response_placeholder.markdown(f'<div class="jarvis-final-box" style="color:red; border: 1px solid red; padding: 15px;">Erro geral na API Groq: {str(e)}</div>', unsafe_allow_html=True)
            except Exception as e:
                response_placeholder.markdown(f'<div class="jarvis-final-box" style="color:red; border: 1px solid red; padding: 15px;">Erro inesperado: {str(e)}</div>', unsafe_allow_html=True)

            # Salva chat
            titulo_chat = st.session_state.messages[0]["content"][:30] + "..." if st.session_state.messages else "Protocolo Ativo"
            salvar_chat(st.session_state.chat_atual, titulo_chat, st.session_state.messages)

    st.session_state.is_thinking = False  # Pausa pensamento
    st.session_state.processed_prompt = None
