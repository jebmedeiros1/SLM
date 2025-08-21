import streamlit as st
import os
import tempfile
from slm import ask_ollama
from agno import agno_filter
from rag import add_documents_to_index, search_similar_documents, read_document
from db import (
    initialize_db,
    create_conversation,
    add_message,
    list_conversations,
    get_conversation_messages,
)

# Inicializações
DOCS_DIR = "docs"
os.makedirs(DOCS_DIR, exist_ok=True)

st.set_page_config(page_title="Oráculo SLM", layout="wide")
initialize_db()

#user = login()
#3if not user:
#    st.stop()
user = "Jefferson"
st.title(f"🧙‍♂️ Oráculo SLM - Bem-vindo, {user}")

# Upload e reindexação
st.sidebar.header("📤 Subir documentos")
uploaded_files = st.sidebar.file_uploader(
    "Selecione documentos (.pdf, .csv, .xls, .xml)", accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        with open(os.path.join(DOCS_DIR, file.name), "wb") as f:
            f.write(file.read())
    st.sidebar.success("Documentos salvos!")

if st.sidebar.button("🔁 Reprocessar documentos"):
    add_documents_to_index(DOCS_DIR)
    st.sidebar.success("Documentos reprocessados!")

# Conversas
st.sidebar.subheader("📚 Suas conversas")
conversations = list_conversations(user)
selected_convo = st.sidebar.selectbox(
    "Selecionar conversa:", ["Nova conversa"] + [f"{c[1]} (ID {c[0]})" for c in conversations]
)

if selected_convo == "Nova conversa":
    new_title = st.text_input("🔤 Título da nova conversa")
    if st.button("Iniciar conversa") and new_title:
        conversation_id = create_conversation(user, new_title)
        st.session_state["conversation_id"] = conversation_id
        st.success(f"Nova conversa '{new_title}' iniciada.")
elif "ID" in selected_convo:
    conversation_id = int(selected_convo.split("ID")[-1].strip(" )"))
    st.session_state["conversation_id"] = conversation_id

conversation_id = None
if "conversation_id" in st.session_state:
    conversation_id = st.session_state["conversation_id"]
    history = get_conversation_messages(conversation_id)
    for sender, content in history:
        role = "user" if sender == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(content)
else:
    st.info("Selecione ou crie uma conversa para começar.")

if conversation_id:
    uploaded_temp = st.file_uploader(
        "📎 Analisar arquivo (não será salvo)",
        type=["pdf", "csv", "xls", "xlsx", "xml"],
    )
    question = st.chat_input("Digite sua pergunta")
    if question:
        add_message(conversation_id, "user", question)
        with st.chat_message("user"):
            st.markdown(question)
        file_context = ""
        if uploaded_temp is not None:
            tmp = tempfile.NamedTemporaryFile(delete=False)
            tmp.write(uploaded_temp.read())
            tmp_path = tmp.name
            tmp.close()
            file_context = read_document(tmp_path)
            os.unlink(tmp_path)
        agno = agno_filter(question)
        if agno:
            add_message(conversation_id, "oracle", agno)
            with st.chat_message("assistant"):
                st.markdown(agno)
        else:
            context, fontes = search_similar_documents(question)
            if file_context:
                context = f"{file_context}\n{context}" if context else file_context
            history_text = "\n".join(
                [f"{s}: {c}" for s, c in get_conversation_messages(conversation_id)]
            )
            prompt = f"{history_text}\n\nContexto:\n{context}\n\n{user}: {question}\nOráculo:"
            resposta = ask_ollama(prompt)
            if fontes:
                resposta += f"\n\n🔎 Fontes: {', '.join(fontes)}"
            add_message(conversation_id, "oracle", resposta)
            with st.chat_message("assistant"):
                st.markdown(resposta)
