import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gpt-oss:20b"

def ask_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        if response.ok:
            return response.json()["response"].strip()
        return f"Erro na resposta do modelo: {response.text}"
    except Exception as e:
        return f"Erro na conexão com o Ollama: {e}"
