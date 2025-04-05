def summarize_text(text: str) -> str:
    """
    Naive summarization by extracting the first 2-3 sentences.
    In production, replace this with a call to an LLM or advanced NLP model.
    """
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    summary = ' '.join(sentences[:3]) if len(sentences) > 2 else text
    return summary
