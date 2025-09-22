import os
from typing import List, Dict

try:
    import google.generativeai as genai
except Exception:  # lib opcional, tratada em runtime
    genai = None  # type: ignore


DEFAULT_MODEL = "gemini-1.5-pro"


def _ensure_configured(api_key: str) -> None:
    if genai is None:
        raise RuntimeError("Biblioteca google-generativeai não instalada. Adicione google-generativeai ao requirements.")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não configurada.")
    genai.configure(api_key=api_key)


def analyze_logs_with_gemini(api_key: str, logs: List[str], model: str = DEFAULT_MODEL, max_chars: int = 120_000) -> Dict:
    """Envia logs para o Gemini e retorna um resumo estruturado.

    - Corta de forma segura para não exceder limites de contexto.
    - Não altera a lógica existente; apenas fornece análise auxiliar.
    """
    _ensure_configured(api_key)

    text = "\n".join(logs)
    if len(text) > max_chars:
        text = text[:max_chars]

    prompt = (
        "Você é um analista de segurança. Leia os logs abaixo e produza: "
        "1) Principais indicadores (IoCs) mencionados. "
        "2) Eventos suspeitos com breve justificativa. "
        "3) Recomendações acionáveis. "
        "Responda em JSON com chaves: indicators, suspicious_events, recommendations.\n\n"
        "Logs:\n" + text
    )

    model_obj = genai.GenerativeModel(model)
    response = model_obj.generate_content(prompt)

    out_text = getattr(response, "text", None) or ""
    return {
        "model": model,
        "output": out_text,
    }


