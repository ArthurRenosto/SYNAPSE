import os
from typing import List, Dict

try:
    import google.generativeai as genai
except Exception:  # lib opcional, tratada em runtime
    genai = None  # type: ignore


DEFAULT_MODEL = "gemini-1.5-flash"  # Modelo mais leve para evitar quota


def _ensure_configured(api_key: str) -> None:
    if genai is None:
        raise RuntimeError("Biblioteca google-generativeai não instalada. Adicione google-generativeai ao requirements.")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não configurada.")
    genai.configure(api_key=api_key)


def analyze_logs_with_gemini(api_key: str, logs: List[str], model: str = "gemini-1.5-flash", max_chars: int = 30_000) -> Dict:
    """Envia logs para o Gemini com otimizações para evitar quota exceeded.
    
    - Usa modelo mais leve (gemini-1.5-flash)
    - Reduz drasticamente o tamanho dos logs
    - Implementa retry com backoff
    - Chunking inteligente de logs
    """
    _ensure_configured(api_key)

    # Reduz logs para evitar quota exceeded
    text = "\n".join(logs)
    if len(text) > max_chars:
        # Pega início e fim dos logs para manter contexto
        half_size = max_chars // 2
        text = text[:half_size] + "\n\n[... logs truncados ...]\n\n" + text[-half_size:]

    prompt = (
        "Analise os logs e liste as vulnerabilidades encontradas. "
        "Seja conciso e direto. Foque apenas nas ameaças mais críticas.\n\n"
        "Logs:\n" + text
    )

    # Retry com backoff exponencial
    import time
    max_retries = 3
    base_delay = 2
    
    for attempt in range(max_retries):
        try:
            model_obj = genai.GenerativeModel(model)
            response = model_obj.generate_content(prompt)
            
            out_text = getattr(response, "text", None) or ""
            return {
                "model": model,
                "output": out_text,
                "attempt": attempt + 1,
                "truncated": len("\n".join(logs)) > max_chars
            }
            
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"[AVISO] Quota exceeded, tentando novamente em {delay}s...")
                    time.sleep(delay)
                    continue
                else:
                    return {
                        "model": model,
                        "output": f"❌ Erro de quota: {error_msg}\n\nTente novamente mais tarde ou use logs menores.",
                        "error": "quota_exceeded",
                        "attempt": attempt + 1
                    }
            else:
                return {
                    "model": model,
                    "output": f"❌ Erro na análise: {error_msg}",
                    "error": "api_error",
                    "attempt": attempt + 1
                }
    
    return {
        "model": model,
        "output": "❌ Falha após múltiplas tentativas",
        "error": "max_retries_exceeded"
    }


def analyze_logs_chunked(api_key: str, logs: List[str], chunk_size: int = 20_000) -> Dict:
    """Analisa logs em chunks menores para evitar quota exceeded."""
    _ensure_configured(api_key)
    
    if not logs:
        return {"model": "gemini-1.5-flash", "output": "Nenhum log fornecido", "chunks": 0}
    
    # Divide logs em chunks menores
    all_text = "\n".join(logs)
    chunks = []
    for i in range(0, len(all_text), chunk_size):
        chunk = all_text[i:i + chunk_size]
        chunks.append(chunk)
    
    results = []
    successful_chunks = 0
    
    for i, chunk in enumerate(chunks):
        try:
            result = analyze_logs_with_gemini(api_key, [chunk], max_chars=chunk_size)
            if result.get("error") != "quota_exceeded":
                results.append(f"--- CHUNK {i+1}/{len(chunks)} ---\n{result['output']}")
                successful_chunks += 1
            else:
                results.append(f"--- CHUNK {i+1}/{len(chunks)} ---\n❌ Quota exceeded neste chunk")
        except Exception as e:
            results.append(f"--- CHUNK {i+1}/{len(chunks)} ---\n❌ Erro: {e}")
    
    return {
        "model": "gemini-1.5-flash",
        "output": "\n\n".join(results),
        "chunks": len(chunks),
        "successful_chunks": successful_chunks,
        "truncated": len(all_text) > chunk_size
    }


