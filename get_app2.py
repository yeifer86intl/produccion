import streamlit as st
import requests
import time

# Configuración de la API
API_BASE_URL = "https://o4zgf7m5obg4x4kruerabsxg240vchpd.lambda-url.us-east-1.on.aws"
API_SUBMIT_QUERY = f"{API_BASE_URL}/submit_query"
API_GET_QUERY = f"{API_BASE_URL}/get_query"

# Inicializar el historial en session_state si no existe
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("💬 RAG Chatbot")
st.write("Escribe una pregunta y el sistema te responderá basado en la base de conocimiento.")

# Campo de entrada para el usuario
query_text = st.text_area("Introduce tu pregunta:")

if st.button("Enviar Consulta"):
    if query_text.strip():
        with st.spinner("Procesando la consulta..."):
            # 1️⃣ Enviar la consulta a la API y obtener el query_id
            response = requests.post(API_SUBMIT_QUERY, json={"query_text": query_text})
            if response.status_code == 200:
                data = response.json()
                query_id = data["query_id"]
                st.session_state.chat_history.append({"role": "user", "text": query_text})

                # 2️⃣ Hacer polling hasta que la respuesta esté lista
                for i in range(30):  # Máximo 30 intentos (~30s)
                    time.sleep(2)  # Esperar 2 segundos antes de intentar nuevamente
                    response = requests.get(API_GET_QUERY, params={"query_id": query_id})
                    if response.status_code == 200:
                        query_data = response.json()
                        if query_data["is_complete"]:
                            bot_response = query_data["answer_text"]
                            st.session_state.chat_history.append({"role": "bot", "text": bot_response})
                            break
                    else:
                        st.error("Error al obtener la respuesta. Inténtalo nuevamente.")
                else:
                    bot_response = "⚠️ No se recibió respuesta a tiempo. Intenta nuevamente más tarde."
                    st.session_state.chat_history.append({"role": "bot", "text": bot_response})
            else:
                st.error("Error al enviar la consulta. Inténtalo nuevamente.")
    else:
        st.warning("Por favor, introduce una consulta.")

# 🗨 Mostrar todo el historial de la conversación
st.subheader("📜 Historial de la Conversación")
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f"👤 **Tú:** {chat['text']}")
    else:
        st.markdown(f"🤖 **Chatbot:** {chat['text']}")