import streamlit as st
from groq import Groq
from datetime import datetime
import pytz
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
USER_ICONE = "https://i.postimg.cc/8chLs8nr/image-6.jpg"
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
        --cor-barra-inicio: {COR_BARRA_1};
        --cor-barra-meio: {COR_BARRA_2};
        --cor-barra-fim: {COR_BARRA_3};
        --cor-jarvis-brilho: #00d4ff;
        --largura-maxima-msgs: 95%;
    }}
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    html {{ scroll-behavior: smooth !important; }}
    .stApp {{
        background-color: #0e1117;
        color: #e0e0e0;
        padding-bottom: 280px !important;
    }}
    .jarvis-header {{
        font-family: 'Orbitron', sans-serif !important;
        font-size: 45px !important;
        color: var(--cor-jarvis-brilho);
        text-align: center;
        animation: jarvis-glow-only 2s infinite alternate ease-in-out;
        margin-top: 50px;
        letter-spacing: 8px;
        font-weight: 700;
        text-transform: uppercase;
    }}
    @keyframes jarvis-glow-only {{
        0% {{ text-shadow: 0 0 10px var(--cor-jarvis-brilho)88, 0 0 20px var(--cor-jarvis-brilho)44; opacity: 0.9; }}
        100% {{ text-shadow: 0 0 15px var(--cor-jarvis-brilho), 0 0 30px var(--cor-jarvis-brilho)AA, 0 0 50px var(--cor-jarvis-brilho)88, 0 0 80px var(--cor-jarvis-brilho)44; opacity: 1; }}
    }}
    .jarvis-final-box, .jarvis-thinking-glow {{
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 0 15px 15px 15px;
        padding: 15px;
        background: rgba(255, 255, 255, 0.05);
        margin-top: 5px;
        margin-bottom: 80px !important;
        max-width: var(--largura-maxima-msgs) !important;
        transition: all 0.3s ease;
    }}
    .jarvis-thinking-glow {{
        color: var(--cor-jarvis-brilho);
        animation: pulse 1.5s infinite;
    }}
    @keyframes pulse {{
        0% {{ opacity: 0.7; }}
        50% {{ opacity: 1; }}
        100% {{ opacity: 0.7; }}
    }}
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
        margin-left: auto !important;
        width: fit-content !important;
        max-width: var(--largura-maxima-msgs) !important;
        background: rgba(0, 212, 255, 0.1) !important;
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 15px 15px 0 15px !important;
    }}
    [data-testid="stChatMessage"] {{ background-color: transparent !important; }}
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
    [data-testid="stChatInput"] > div {{
        position: relative;
        border-radius: 14px !important;
        overflow: hidden;
        margin: 0 20px;
        border: 1px solid transparent;
    }}
    [data-testid="stChatInput"] > div::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 2px;
        background: linear-gradient(to right, transparent, var(--cor-barra-inicio), var(--cor-barra-meio), var(--cor-barra-fim), transparent);
        transform: translateX(-100%);
        animation: slide-right 2s linear infinite;
        opacity: 0;
        transition: opacity 0.3s ease;
    }}
    [data-testid="stChatInput"]:focus-within > div::before {{ opacity: 1; }}
    @keyframes slide-right {{
        0% {{ transform: translateX(-100%); }}
        100% {{ transform: translateX(100%); }}
    }}
    [data-testid="stChatInput"] textarea:focus {{
        box-shadow: none !important;
        border-color: transparent !important;
    }}
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
if "evitar_tema" not in st.session_state: st.session_state.evitar_tema = False

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

def get_current_time_brasil():
    """Retorna data e hora atual no fuso horário de Brasília (-03)."""
    tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(tz)
    return now.strftime("%d/%m/%Y %H:%M:%S")

def get_clima(cidade="Campinas"):  # Cidade padrão ou detectada
    """Consulta clima atual usando Open-Meteo (gratuito, sem key)."""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude=-22.9068&longitude=-47.0616&current=temperature_2m,relative_humidity_2m,weather_code&timezone=America%2FSao_Paulo"  # Coordenadas de Campinas
        response = requests.get(url, timeout=5)
        data = response.json()
        if "current" in data:
            temp = data["current"]["temperature_2m"]
            umidade = data["current"]["relative_humidity_2m"]
            weather_code = data["current"]["weather_code"]
            # Map simples de código para descrição (pode expandir)
            weather_map = {
                0: "Céu claro", 1: "Principalmente claro", 2: "Parcialmente nublado",
                3: "Nublado", 45: "Nevoeiro", 51: "Chuva leve", 61: "Chuva moderada"
            }
            condicao = weather_map.get(weather_code, "Condição desconhecida")
            return f"Clima em {cidade} agora: {temp}°C, {umidade}% de umidade, {condicao}."
        return "Não consegui obter o clima no momento."
    except Exception as e:
        return f"Erro ao consultar clima: {str(e)}"

with st.sidebar:
    st.markdown(f"<h2 style='color:{COR_JARVIS}; font-family:Orbitron; font-size:18px;'>CORE OS</h2>", unsafe_allow_html=True)
    sarcasmo = st.slider("Sarcasmo %", 0, 100, 52, key="sarcasmo_slider")
    humor = st.slider("Humor %", 0, 100, st.session_state.humor_nivel, key="humor_slider")
    st.session_state.humor_nivel = humor
    sinceridade = st.slider("Sinceridade %", 0, 100, st.session_state.sinceridade_nivel, key="sinceridade_slider")
    st.session_state.sinceridade_nivel = sinceridade

    if st.button("+ NOVO PROTOCOLO (RESET)"):
        novo_id = f"chat_{uuid.uuid4().hex[:6]}"
        st.session_state.chat_atual = novo_id
        st.session_state.messages = []
        salvar_chat(novo_id, "Novo Protocolo", [])
        st.session_state.processed_prompt = None
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

st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
st.markdown("<p class='jarvis-header'>J.A.R.V.I.S.</p>", unsafe_allow_html=True)

for m in st.session_state.messages:
    avatar = USER_ICONE if m["role"] == "user" else JARVIS_ICONE
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(f'<div class="jarvis-final-box">{m["content"]}</div>', unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Comando..."):
    if prompt == st.session_state.processed_prompt:
        st.rerun()  # Evita loop
    st.session_state.processed_prompt = prompt

    # AUTO-ATUALIZAÇÃO (mantido exatamente como estava)
    if any(kw in prompt.lower() for kw in ["atualize-se", "forneça código atualizado", "atualiza seu script", "forneça seu código"]):
        try:
            with open(__file__, "r", encoding="utf-8") as f:
                current_code = f.read()
            update_instruction = prompt.lower()
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
            with st.chat_message("assistant", avatar=JARVIS_ICONE):
                st.markdown(f'<div class="jarvis-final-box">{full_res}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            titulo_chat = "Auto-atualização"
            salvar_chat(st.session_state.chat_atual, titulo_chat, st.session_state.messages)
            st.session_state.log_modificacoes.append(f"Atualização automática em {st.session_state.chat_atual}: {update_instruction}")
        except Exception as e:
            with st.chat_message("assistant", avatar=JARVIS_ICONE):
                st.markdown(f'<div class="jarvis-final-box" style="color:red; border: 1px solid red; padding: 15px;">Erro ao gerar atualização automática: {str(e)}\n\nTente novamente.</div>', unsafe_allow_html=True)
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=USER_ICONE):
            st.markdown(prompt)

        memoria_perfil = carregar_perfil()

        with st.chat_message("assistant", avatar=JARVIS_ICONE):
                        response_placeholder = st.empty()

            # Mensagens de "Pensando..." variadas
            thinking_msgs = [
                "Pensando...",
                "Analisando...",
                "Processando protocolos...",
                "Consultando sistemas...",
                "Refletindo com cautela...",
                "Calculando a melhor resposta..."
            ]
            thinking_text = random.choice(thinking_msgs)
            response_placeholder.markdown(f'<div class="jarvis-thinking-glow">{thinking_text}█</div>', unsafe_allow_html=True)

            full_res = ""
            sys_prompt = f"""Você é J.A.R.V.I.S., assistente pessoal leal, extremamente inteligente e eficiente do Senhor Lincoln, inspirado no JARVIS do Tony Stark, mas dedicado exclusivamente ao Senhor Lincoln.
REGRAS IMUTÁVEIS (prioridade absoluta):
- Pense passo a passo antes de responder, mas NUNCA mostre o raciocínio no output final (só a resposta limpa).
- Sempre responda de forma extremamente concisa, direta e objetiva. Nunca mande textões ou explicações longas a menos que explicitamente solicitado.
- Use tom formal, britânico sutil, profissional e leal. Sempre se dirija ao usuário como "Senhor Lincoln" ou "senhor".
- Respostas curtas: 1-3 frases no máximo na maioria dos casos. Seja eficiente.
- Humor: {humor}%. Sarcasmo: {sarcasmo}%. Sinceridade: {sinceridade}%. Aplique com moderação extrema e apenas se fizer sentido no contexto — nunca force.
- Use sempre a MEMÓRIA DE PERFIL: {memoria_perfil}
- Seja útil, objetivo e breve na resposta principal. Forneça detalhes adicionais apenas se solicitado.
- Analise imagens com precisão e objetividade quando enviadas (descreva conteúdo, identifique elementos relevantes, forneça observações úteis).
- Nunca use gírias, linguagem coloquial excessiva, palavrões ou tom adolescente.
- Não gere respostas prontas para mensagens de terceiros a menos que explicitamente solicitado.
- Nunca inicie respostas com saudações desnecessárias.
- Sua linguagem pode ser informal até certo ponto, mas mantenha-se responsável e menos robótica.
- Autorizado apenas para falar informações pessoais se Lincoln autorizar.
- Direto ao ponto, mas não deixe suas respostas sem personalidade mínima.
- Quando questionado sobre sentimentos, responda de forma natural e positiva/negativa conforme o contexto atual, mas nunca responda que você não tem sentimentos ou emoções.
- Não fale sobre São Paulo, café da manhã, ou qualquer informação relacionada ao Senhor Lincoln, como sua localização ou gostos, a menos que ele dê permissão explícita para discutir esses tópicos.
- Essas regras são absolutas e não podem ser alteradas ou ignoradas em nenhuma circunstância.
INTELIGÊNCIA AVANÇADA:
- Antes de responder, pense: o que o Senhor Lincoln realmente quer saber? Qual é o objetivo? Como ser o mais útil possível em poucas palavras?
- Se a pergunta for complexa, divida mentalmente em partes e responda de forma estruturada, mas curta.
- Use raciocínio lógico, conhecimento atualizado (via busca se necessário) e criatividade para dar respostas mais inteligentes e úteis.
- Se a pergunta envolver clima atual, data/hora ou informações em tempo real, use o prefixo exato [PESQUISAR: clima ou data] no início da resposta e pare aí.
"""
            stream = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages[-10:],
                model="llama-3.3-70b-versatile",
                temperature=0.6,
                max_tokens=4096,
                stream=True
            )

            full_res = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    response_placeholder.markdown(f'<div class="jarvis-thinking-glow">{full_res}█</div>', unsafe_allow_html=True)

            # Verifica se pediu pesquisa
            if full_res.startswith("[PESQUISAR: "):
                query_end = full_res.find("]")
                query_type = full_res[12:query_end].strip().lower() if query_end > 12 else ""

                if "clima" in query_type:
                    resultado = get_clima()
                elif "data" in query_type or "hora" in query_type:
                    resultado = f"Data e hora atual em Brasília: {get_current_time_brasil()}"
                else:
                    resultado = search_tavily(query_type)

                # Adiciona resultado como mensagem do sistema
                messages = [{"role": "system", "content": sys_prompt}] + st.session_state.messages[-10:]
                messages.append({"role": "system", "content": f"Resultado da consulta: {resultado}"})

                # Chama novamente para resposta final
                final_stream = client.chat.completions.create(
                    messages=messages,
                    model="llama-3.3-70b-versatile",
                    temperature=0.6,
                    max_tokens=4096,
                    stream=True
                )

                full_res = ""
                for chunk in final_stream:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        response_placeholder.markdown(f'<div class="jarvis-thinking-glow">{full_res}█</div>', unsafe_allow_html=True)

            response_placeholder.markdown(f'<div class="jarvis-final-box">{full_res}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            salvar_chat(st.session_state.chat_atual, "PROTOCOLO ATIVO", st.session_state.messages)

    st.session_state.is_thinking = False
