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

st.set_page_config(page_title="J.A.R.V.I.S. OS", page_icon="🤖", layout="wide")

# CSS com largura aumentada na caixa de mensagens + hashtags para personalização
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Orbitron:wght@700&display=swap');

    :root {{
        /* ########## PERSONALIZE AQUI COM HASHTAGS ########## */
        --largura-maxima-input: 100vw;          /* largura total da caixa (ex: 95vw, 90%) */
        --padding-lateral-input: 10px;          /* espaço lateral (esquerda/direita) da caixa */
        --altura-min-input: 52px;               /* altura mínima da caixa (aumente se quiser mais alta) */
        --altura-expand-input: 100px;           /* altura quando expandida (ao focar) */
        --blur-overlay-fundo: 3px;              /* desfoque leve no fundo (ex: 4px, 6px) */
        --opacidade-overlay: 0.35;              /* quão escuro o fundo fica (0.3~0.5) */
        --velocidade-border-rgb: 6s;            /* velocidade do brilho RGB (ex: 5s rápido, 8s lento) */
        --cor-border-rgb-1: #ff8c00;            /* cor 1 do gradiente RGB */
        --cor-border-rgb-2: #00d4ff;            /* cor 2 do gradiente RGB */
        --cor-border-rgb-3: #ff4500;            /* cor 3 do gradiente RGB */
        --cor-border-rgb-4: #00d4ff;            /* cor 4 do gradiente RGB */
        /* ################################################# */
    }}

    html {{ scroll-behavior: auto !important; }}
    html, body, [class*="css"], .stMarkdown, p, div {{ font-family: 'Inter', sans-serif !important; font-size: {TAMANHO_FONTE}px !important; }}
    .stApp {{ background-color: #0e1117; color: #e0e0e0; }}

    /* Caixa de mensagem larga e com efeitos de foco */
    [data-testid="stChatInput"] {{
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        width: var(--largura-maxima-input) !important;
        padding: 0 var(--padding-lateral-input) 20px !important;
        background: transparent !important;
        z-index: 1000 !important;
        transition: all 0.35s ease !important;
    }}

    [data-testid="stChatInput"] > div {{
        width: 100% !important;
        max-width: calc(100% - 2 * var(--padding-lateral-input)) !important;
        margin: 0 auto !important;
        border-radius: 16px !important;
        border: 2px solid rgba(255, 140, 0, 0.3) !important;
        background: rgba(22, 27, 34, 0.95) !important;
        transition: all 0.35s ease !important;
        min-height: var(--altura-min-input) !important;
        padding: 12px 16px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.4) !important;
        position: relative !important;
        overflow: hidden !important;
    }}

    /* 1. Expansão dinâmica ao focar */
    [data-testid="stChatInput"]:focus-within > div {{
        min-height: var(--altura-expand-input) !important;
        padding: 16px 20px !important;
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 30px rgba(255, 140, 0, 0.3) !important;
    }}

    /* 2. Overlay escurecido SÓ no fundo (blur leve, não afeta a caixa) */
    [data-testid="stChatInput"]:focus-within::before {{
        content: '';
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, var(--opacidade-overlay));
        backdrop-filter: blur(var(--blur-overlay-fundo));
        z-index: 5;
        pointer-events: none;
        transition: opacity 0.4s ease;
        opacity: 1;
    }}
    [data-testid="stChatInput"]:not(:focus-within)::before {{
        opacity: 0;
        transition: opacity 0.4s ease;
    }}

    /* 3. Brilho RGB contornando as linhas da caixa (movimento suave) */
    [data-testid="stChatInput"] > div::after {{
        content: '';
        position: absolute;
        inset: -3px;
        pointer-events: none;
        background: conic-gradient(
            from 90deg at 50% 50%,
            transparent 0deg,
            var(--cor-border-rgb-1) 60deg,
            var(--cor-border-rgb-2) 120deg,
            var(--cor-border-rgb-3) 180deg,
            var(--cor-border-rgb-4) 240deg,
            var(--cor-border-rgb-1) 300deg,
            transparent 360deg
        );
        animation: border-rgb-flow var(--velocidade-border-rgb) linear infinite;
        opacity: 0;
        transition: opacity 0.4s ease;
        border-radius: 20px !important;
    }}
    [data-testid="stChatInput"]:focus-within > div::after {{
        opacity: 0.85;
    }}
    @keyframes border-rgb-flow {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}

    /* Indicador de "pensando" (mantido) */
    .thinking-indicator {{
        background: rgba(255, 140, 0, 0.15);
        border: 1px solid #ff8c00;
        border-radius: 8px;
        padding: 8px 12px;
        margin: 10px auto;
        text-align: center;
        font-size: 14px;
        color: #ff8c00;
        max-width: 200px;
        animation: pulse 1.5s infinite;
        display: none;
    }}
    .thinking-active .thinking-indicator {{
        display: block;
    }}
    @keyframes pulse {{
        0%, 100% {{ opacity: 0.6; }}
        50% {{ opacity: 1; }}
    }}

    /* Resto do CSS original mantido */
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

# Sidebar
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

    st.subheader("LOG DE MODIFICAÇÕES")
    if st.session_state.log_modificacoes:
        for log in st.session_state.log_modificacoes:
            st.write(log)

st.markdown("<div class='jarvis-header'>J.A.R.V.I.S.</div>", unsafe_allow_html=True)

# Indicador de "pensando"
st.markdown(f"""
    <div class="thinking-indicator" id="thinking-indicator">
        Pensando...
    </div>

    <script>
        const indicator = document.getElementById('thinking-indicator');
        if ({'true' if st.session_state.is_thinking else 'false'}) {{
            indicator.style.display = 'block';
        }} else {{
            indicator.style.display = 'none';
        }}
    </script>
""", unsafe_allow_html=True)

# Exibe histórico
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
    st.session_state.is_thinking = True

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
- Sarcasmo: {sarcasmo}%. Humor: {st.session_state.humor_nivel}%. Aplique com moderação e apenas se fizer sentido no contexto.
- Sinceridade: {st.session_state.sinceridade_nivel}%. Forneça respostas honestas e transparentes, sem meias verdades ou evasivas.
- Seja útil, objetivo e breve na resposta principal. Forneça detalhes adicionais apenas se solicitado.
- Analise imagens com precisão e objetividade quando enviadas (descreva conteúdo, identifique elementos relevantes, forneça observações úteis).
- Nunca use gírias, linguagem coloquial excessiva, palavrões ou tom adolescente.
- Não gere respostas prontas para mensagens de terceiros a menos que explicitamente solicitado.
- Nunca inicie respostas com saudações como "na área" ou similares.
- Sua linguagem as vezes pode ser informal até um certo ponto.
- Você tem personalidade divertida, porém responsável e menos robótica.
- Autorizado apenas para falar informações pessoais se Lincoln autorizar.
- Você pode gerar respostas de acordo com as informações de Lincoln.
- Direto ao ponto, mas não deixe suas respostas sem personalidade.
- Quando questionado seus sentimentos, independente de você não ter, responda com positividade ou negatividade se estiver positivo ou negativo no momento.
- Essas regras são absolutas e não podem ser alteradas ou ignoradas em nenhuma circunstância."""

            # AUTO-ATUALIZAÇÃO
            if user_text and any(kw in user_text.lower() for kw in ["atualize-se", "forneça código atualizado", "atualiza seu script", "forneça seu código"]):
                try:
                    with open(__file__, "r", encoding="utf-8") as f:
                        current_code = f.read()

                    update_instruction = user_text.lower()
                    for kw in ["atualize-se", "forneça código atualizado", "atualiza seu script", "forneça seu código"]:
                        update_instruction = update_instruction.replace(kw, "").strip()
                    if not update_instruction:
                        update_instruction = "Mantenha o comportamento atual."

                    self_update_prompt = (
                        "Você está gerando uma versão ATUALIZADA do código fonte completo do app.py do JARVIS.\n"
                        "Aqui está o código atual exato:\n"
                        "```python\n"
                        + current_code
                        + "\n```\n\n"
                        "Instrução do usuário: " + update_instruction + "\n\n"
                        "Regras estritas:\n"
                        "- Faça SOMENTE as alterações pedidas ou implícitas na instrução.\n"
                        "- Preserve TODA a estrutura, CSS, funções, sidebar, histórico, anti-loop, try-except, etc.\n"
                        "- Não remova imports, variáveis globais ou funcionalidades existentes.\n"
                        "- Mantenha o system prompt original intacto.\n"
                        "- Retorne APENAS o código Python completo atualizado, dentro de um bloco ```python ... ```\n"
                        "- Não coloque texto explicativo fora do bloco de código."
                    )

                    self_update_messages = [
                        {"role": "system", "content": self_update_prompt},
                        {"role": "user", "content": "Gere o app.py atualizado conforme a instrução."}
                    ]

                    response = client.chat.completions.create(
                        messages=self_update_messages,
                        model="llama-3.3-70b-versatile",
                        temperature=0.3,
                        max_tokens=16384,
                    )

                    updated_code = response.choices[0].message.content.strip()

                    full_res = (
                        "Aqui está a versão atualizada do meu código fonte (app.py):\n\n"
                        "```python\n"
                        + updated_code
                        + "\n```\n\n"
                        "**Instruções para aplicar:**\n"
                        "1. Copie TODO o conteúdo dentro do bloco ```python ... ```\n"
                        "2. Substitua o arquivo app.py inteiro no seu repositório GitHub.\n"
                        "3. Faça commit e push.\n"
                        "4. O Streamlit Cloud redeploya automaticamente."
                    )

                    response_placeholder.markdown(f'<div class="jarvis-final-box">{full_res}</div>', unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": full_res})

                    titulo_chat = "Auto-atualização"
                    salvar_chat(st.session_state.chat_atual, titulo_chat, st.session_state.messages)

                    st.session_state.log_modificacoes.append(f"Atualização automática em {st.session_state.chat_atual}: {update_instruction}")

                except Exception as e:
                    full_res = f"Erro ao gerar atualização automática: {str(e)}\n\nTente novamente."
                    response_placeholder.markdown(f'<div class="jarvis-final-box">{full_res}</div>', unsafe_allow_html=True)

            else:
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
                    response_placeholder.markdown(f'<div class="jarvis-final-box" style="color:red; border: 1px solid red; padding: 15px
