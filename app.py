import streamlit as st
from groq import Groq
import os

# 1. Configuração da Página
st.set_page_config(page_title="J.A.R.V.I.S.", page_icon="🤖")

# 2. CSS Customizado (Mantendo seu estilo de balões e cores frias)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { color: #00d4ff; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stChatMessage"] { border-radius: 15px; margin-bottom: 10px; width: 80%; }
    
    /* Balão do Lincoln (Direita) - Cores Frias */
    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {
        margin-left: auto;
        background-color: #1d2b3a;
        border: 1px solid #00d4ff55;
    }

    /* Balão do JARVIS (Esquerda) */
    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from assistant"]) {
        margin-right: auto;
        background-color: #161b22;
        border: 1px solid #30363d;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("J.A.R.V.I.S.")
st.caption("Protocolo de Identidade Ativo - Senhor Lincoln")

# 3. Carregamento do Perfil Personalizado
def carregar_perfil():
    try:
        if os.path.exists("perfil.txt"):
            with open("perfil.txt", "r", encoding="utf-8") as f:
                conteudo = f.read()
                if conteudo.strip(): # Verifica se não está vazio
                    return conteudo
        return "Perfil não encontrado no servidor."
    except Exception as e:
        return f"Erro ao ler perfil: {e}"
        
perfil_contexto = carregar_perfil()

# 4. Conexão com Groq
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = "SUA_CHAVE_AQUI"

client = Groq(api_key=api_key)

# 5. Memória da Conversa
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Interação
if prompt := st.chat_input("Em que posso ser útil, Senhor?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # O JARVIS agora usa o seu perfil em cada resposta
            system_prompt = f"""
            Você é o JARVIS. Responda de forma elegante, técnica e curta.
            Siga rigorosamente este contexto sobre o usuário: {perfil_contexto}.
            Lembre-se: Ele é organizado, perfeccionista e prefere cores frias.
            Se ele falar de carros, lembre-se que ele não entende e não tem interesse.
            """
            
            full_messages = [{"role": "system", "content": system_prompt}] + [
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
            st.error(f"Erro nos sistemas: {e}")
