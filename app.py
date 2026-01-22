import streamlit as st
from groq import Groq

# 1. Configuração visual da página (O "Corpo" do Jarvis)
st.set_page_config(page_title="J.A.R.V.I.S.", page_icon="🤖")

# Estilo para deixar com cara de terminal de tecnologia
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stChatMessage { border-radius: 15px; border: 1px solid #00d4ff33; }
    h1 { color: #00d4ff; text-shadow: 2px 2px #000; }
    </style>
    """, unsafe_allow_html=True)

st.title("J.A.R.V.I.S. 🛡️")
st.caption("Protocolo de Interface Web - Senhor Lincoln")

# 2. Conexão com o cérebro (Groq)
# No Streamlit Cloud, vamos usar 'secrets' para a chave ficar protegida
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    # Se você for testar localmente, coloque a chave aqui
    api_key = st.secrets["GROQ_API_KEY"]

client = Groq(api_key=api_key)

# 3. Memória da conversa (Para ele não esquecer o que você disse na mensagem anterior)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe o histórico de mensagens na tela
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Campo de entrada (Onde você digita)
if prompt := st.chat_input("Em que posso ajudar, Senhor?"):
    # Adiciona sua pergunta ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Resposta do Jarvis
    with st.chat_message("assistant"):
        try:
            # Instrução de Personalidade
            instrucoes = "Você é o JARVIS. Responda de forma elegante, curta, técnica e chame o usuário de Senhor Lincoln. Foque em ser útil e direto."
            
            full_messages = [{"role": "system", "content": instrucoes}] + [
                {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
            ]

            completion = client.chat.completions.create(
                messages=full_messages,
                model="llama-3.1-8b-instant",
            )
            
            response = completion.choices[0].message.content
            st.markdown(response)
            
            # Guarda a resposta dele na memória
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Senhor, tive um problema no servidor: {e}")
