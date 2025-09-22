#!/usr/bin/env python3
"""
Script para executar análise automática com Gemini
Importa logs automaticamente e executa análise com prompt específico
"""
import os
import sys
import subprocess
from pathlib import Path

# Adiciona o diretório do projeto ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    print("="*60)
    print("SYNAPSE - ANÁLISE AUTOMÁTICA COM GEMINI")
    print("="*60)
    print("Este script irá:")
    print("1. Importar logs automaticamente")
    print("2. Executar análise tradicional com regex")
    print("3. Executar análise com Gemini: 'analise os logs e liste as vulnerabilidades'")
    print("="*60)
    
    # Diretório de logs padrão
    logs_dir = PROJECT_ROOT / "logs"
    if not logs_dir.exists():
        logs_dir.mkdir()
        print(f"Criado diretório de logs: {logs_dir}")
    
    # Busca arquivos de log
    log_files = []
    for ext in ["*.log", "*.txt", "*.json", "*.jsonl", "*.csv"]:
        log_files.extend(logs_dir.glob(ext))
    
    if not log_files:
        print(f"Nenhum arquivo de log encontrado em: {logs_dir}")
        print("Coloque seus arquivos de log nesse diretório e execute novamente.")
        return 1
    
    print(f"Encontrados {len(log_files)} arquivos de log:")
    for f in log_files:
        print(f"  - {f.name}")
    
    # Executa análise com Gemini
    backend_dir = PROJECT_ROOT / "synapse_siem" / "backend"
    main_py = backend_dir / "main.py"
    
    cmd = [
        sys.executable, str(main_py),
        str(logs_dir),
        "--gemini",  # Flag para análise com Gemini
        "--formats", "json,txt",
        "--output-dir", str(backend_dir / "reports")
    ]
    
    print(f"\nExecutando: {' '.join(cmd)}")
    print("="*60)
    
    try:
        result = subprocess.run(cmd, cwd=str(backend_dir))
        return result.returncode
    except KeyboardInterrupt:
        print("\nCancelado pelo usuário.")
        return 130
    except Exception as e:
        print(f"Erro ao executar análise: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
