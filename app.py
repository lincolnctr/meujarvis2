import streamlit as st
from groq import Groq

# 1. Configuração da Página (Sem o escudo agora)
st.set_page_config(page_title="J.A.R.V.I.S.", page_icon="🤖")

# 2. CSS Customizado para alinhar os balões (Direita para Usuário, Esquerda para Jarvis)
st.markdown("""
    <style>
    /* Fundo do App */
    .stApp { background-color: #0e1117; }
    
    /* Título */
    h1 { color: #00d4ff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }

    /* Alinhamento das mensagens */
    [data-testid="stChatMessage"] {
        border-radius: 15px;
        margin-bottom: 10px;
        width: 80%;
    }

    /* Estilo para a mensagem do USUÁRIO (Direita) */
    [data-testid="chatAvatarIcon-user"] {
        display: none;
    }
    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {
        margin-left: auto;
        background-color: #1d2b3a;
        border: 1px solid #00d4ff55;
    }

    /* Estilo para a mensagem do ASSISTENTE (Esquerda) */
    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from assistant"]) {
        margin-right: auto;
        background-color: #161b22;
        border: 1px solid #30363d;
    }
    
    /* Esconde o menu e o footer do Streamlit para ficar mais limpo */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("J.A.R.V.I.S.")
st.caption("Protocolo de Interface - Senhor Lincoln")

# 3. Conexão com a Chave (Usando Secrets)
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = "SUA_CHAVE_AQUI"

client = Groq(api_key=api_key)

# 4. Memória da Conversa
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe as mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Entrada do Usuário
if prompt := st.chat_input("Comande o sistema..."):
    # Salva e exibe mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Resposta do Jarvis
    with st.chat_message("assistant"):
        try:
            instrucoes = "Você é o JARVIS. Responda de forma elegante, curta, técnica e chame o usuário de Senhor Lincoln."
            
            full_messages = [{"role": "system", "content": instrucoes}] + [
                {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
            ]

            completion = client.chat.completions.create(
                messages=full_messages,
                model="llama-3.1-8b-instant",
            )
            
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Erro no sistema: {e}")
