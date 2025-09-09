import os
import shutil
import hashlib
from typing import Iterable, List


LOG_EXTENSIONS = {".log", ".txt", ".json", ".jsonl", ".csv"}


def find_log_files(paths: Iterable[str]) -> List[str]:
    files: List[str] = []
    for p in paths:
        if os.path.isfile(p):
            files.append(os.path.abspath(p))
        elif os.path.isdir(p):
            for root, _dirs, filenames in os.walk(p):
                for name in filenames:
                    ext = os.path.splitext(name)[1].lower()
                    if ext in LOG_EXTENSIONS:
                        files.append(os.path.abspath(os.path.join(root, name)))
        else:
            continue
    return sorted(set(files))


def _hash_path(path: str) -> str:
    h = hashlib.sha256(path.encode("utf-8", errors="ignore")).hexdigest()
    return h[:8]


def copy_logs_to_directory(paths: Iterable[str], destination_directory: str) -> List[str]:
    """
    Copia arquivos de log para um diretório de destino, evitando colisões de nomes
    ao anexar um hash curto baseado no caminho de origem.

    Retorna a lista de caminhos de destino copiados.
    """
    os.makedirs(destination_directory, exist_ok=True)
    copied: List[str] = []
    for src in paths:
        if not os.path.isfile(src):
            continue
        base = os.path.basename(src)
        name, ext = os.path.splitext(base)
        suffix = _hash_path(src)
        dst_name = f"{name}_{suffix}{ext}"
        dst_path = os.path.join(destination_directory, dst_name)
        try:
            shutil.copy2(src, dst_path)
            copied.append(os.path.abspath(dst_path))
        except Exception:
            # ignora arquivos que falharem na cópia
            continue
    return copied




