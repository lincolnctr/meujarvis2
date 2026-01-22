import streamlit as st
from groq import Groq
import os

# 1. Configuração da Página
st.set_page_config(page_title="J.A.R.V.I.S.", page_icon="🤖")

# 2. CSS (Mantendo seu estilo)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { color: #00d4ff; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stChatMessage"] { border-radius: 15px; margin-bottom: 10px; width: 80%; }
    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {
        margin-left: auto; background-color: #1d2b3a; border: 1px solid #00d4ff55;
    }
    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from assistant"]) {
        margin-right: auto; background-color: #161b22; border: 1px solid #30363d;
    }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("J.A.R.V.I.S.")
st.caption("Protocolo de Memória Persistente Ativo")

# 3. Funções de Memória (Arquivos)
def carregar_perfil():
    if os.path.exists("perfil.txt"):
        with open("perfil.txt", "r", encoding="utf-8") as f:
            return f.read()
    return "Lincoln, brasileiro, organizado."

# Nova função para salvar o histórico no disco
def salvar_historico(mensagens):
    with open("historico.json", "w", encoding="utf-8") as f:
        import json
        json.dump(mensagens, f)

# Nova função para carregar o histórico do disco
def carregar_historico():
    if os.path.exists("historico.json"):
        import json
        with open("historico.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

perfil_contexto = carregar_perfil()

# 4. Inicialização da Sessão com Memória
if "messages" not in st.session_state:
    st.session_state.messages = carregar_historico()

# Botão para limpar a memória (caso o Senhor queira resetar o sistema)
if st.sidebar.button("Limpar Memória"):
    st.session_state.messages = []
    if os.path.exists("historico.json"):
        os.remove("historico.json")
    st.rerun()

# Exibe o histórico salvo
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Conexão Groq
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = "SUA_CHAVE_AQUI"

client = Groq(api_key=api_key)

# 6. Interação
if prompt := st.chat_input("Comande, Senhor Lincoln..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            system_prompt = f"""
            Você é o JARVIS. Responda de forma elegante, técnica e curta.
            Contexto: {perfil_contexto}.
            Regras: Seja direto, sem cortesias inúteis. Não invente capacidades físicas.
            Sempre chame o usuário de Senhor Lincoln.
            """
            
            full_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

            completion = client.chat.completions.create(
                messages=full_messages,
                model="llama-3.1-8b-instant",
            )
            
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Salva no arquivo após cada resposta
            salvar_historico(st.session_state.messages)
            
        except Exception as e:
            st.error(f"Erro: {e}")
