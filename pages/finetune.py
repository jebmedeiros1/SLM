import streamlit as st
import os

st.set_page_config(page_title="Fine-tuning SLM", layout="wide")

st.title("🎯 Fine-tuning do SLM")

st.write("Envie um conjunto de dados para ajustar o modelo. Este é um protótipo e não executa o treinamento real.")

uploaded_dataset = st.file_uploader("Dataset em JSONL", type=["jsonl"])
model_name = st.text_input("Nome do modelo gerado", "slm-finetuned")

if st.button("Iniciar fine-tuning"):
    if uploaded_dataset is None:
        st.error("Envie um arquivo de dataset primeiro.")
    else:
        with open("temp_dataset.jsonl", "wb") as f:
            f.write(uploaded_dataset.getbuffer())
        st.success(f"Fine-tuning iniciado para criar o modelo '{model_name}'.")
