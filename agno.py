def agno_filter(question: str) -> str:
    if "devo" in question.lower():
        return "Isso parece uma decisão importante. Quer compartilhar mais contexto?"
    return ""
