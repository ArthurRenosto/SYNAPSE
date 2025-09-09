#!/usr/bin/env python3
import argparse
import json
import os
import sys
from typing import List

# Permite executar este arquivo diretamente de dentro de `backend/`
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from synapse_siem.backend.analyzer import LogAnalyzer
from synapse_siem.backend.report import ReportWriter
from synapse_siem.backend.utils import find_log_files, copy_logs_to_directory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="SYNAPSE - Analisador de Logs (SIEM simplificado)",
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="Arquivos ou diretórios de logs para analisar (se vazio, modo interativo)",
    )
    parser.add_argument(
        "--rules",
        default=os.path.join(os.path.dirname(__file__), "rules.json"),
        help="Caminho do arquivo de regras (JSON)",
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join(os.path.dirname(__file__), "reports"),
        help="Diretório de saída para os relatórios (padrão: backend/reports)",
    )
    parser.add_argument(
        "--formats",
        default="json,md,csv,txt",
        help="Formatos de saída: json,md,csv,txt (separados por vírgula)",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=0,
        help="Limita o número de linhas analisadas por arquivo (0 = sem limite)",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Encoding padrão para leitura dos arquivos de log",
    )
    parser.add_argument(
        "--import-to",
        default="",
        help="Diretório para importar (copiar) os logs antes da análise",
    )
    parser.add_argument(
        "--import-only",
        action="store_true",
        help="Apenas importa (copia) os logs para o diretório indicado e encerra",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Abre seletor de arquivos para escolher logs via interface gráfica",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # Modo GUI/Interativo: se nenhum caminho for informado ou se --gui for usado, abre seletor
    if args.gui or not args.inputs:
        selected: List[str] = []
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.update()
            selected_tuple = filedialog.askopenfilenames(
                title="Selecionar arquivos de log",
                filetypes=[
                    ("Logs", "*.log *.txt *.json *.jsonl *.csv"),
                    ("Todos os arquivos", "*.*"),
                ],
            )
            selected = list(selected_tuple)
            root.destroy()
        except Exception:
            # Fallback para prompt de texto se GUI indisponível
            try:
                user_input = input("Informe os caminhos de logs (separados por espaço ou vírgula): ").strip()
            except KeyboardInterrupt:
                print("\nCancelado pelo usuário.")
                return 130
            if user_input:
                if "," in user_input:
                    selected = [p.strip() for p in user_input.split(",") if p.strip()]
                else:
                    selected = [p.strip() for p in user_input.split() if p.strip()]
        if not selected and not args.inputs:
            print("Nenhum arquivo selecionado. Encerrando.")
            return 2
        if selected:
            args.inputs = selected

    inputs: List[str] = []
    for path in args.inputs:
        if not os.path.exists(path):
            print(f"[ERRO] Caminho não encontrado: {path}", file=sys.stderr)
            return 1
        inputs.append(path)

    log_files = find_log_files(inputs)
    if not log_files:
        print("[AVISO] Nenhum arquivo de log encontrado.")
        return 0

    os.makedirs(args.output_dir, exist_ok=True)

    # Pasta padrão de imports, caso não definida
    default_imports_dir = os.path.join(PROJECT_ROOT, "imports")

    # Importação de logs (GUI sempre importa; linha de comando importa quando --import-to)
    if args.import_to or args.gui:
        dest_dir = args.import_to or default_imports_dir
        imported = copy_logs_to_directory(log_files, dest_dir)
        print(json.dumps({
            "imported_count": len(imported),
            "destination": os.path.abspath(dest_dir),
            "files": imported,
        }, ensure_ascii=False, indent=2))
        if args.import_only:
            return 0
        # se não for import-only, passa a analisar os arquivos importados
        if imported:
            log_files = imported

    analyzer = LogAnalyzer(rules_path=args.rules, default_encoding=args.encoding)
    findings = analyzer.analyze_files(log_files, max_lines=args.max_lines)

    # Saídas
    formats = {fmt.strip().lower() for fmt in args.formats.split(",") if fmt.strip()}
    writer = ReportWriter(output_dir=args.output_dir)

    base_name = "synapse_report"
    if "json" in formats:
        writer.write_json(findings, f"{base_name}.json")
    if "csv" in formats:
        writer.write_csv(findings, f"{base_name}.csv")
    if "md" in formats or "markdown" in formats:
        writer.write_markdown(findings, f"{base_name}.md")
    if "txt" in formats:
        writer.write_txt_simple(findings, f"{base_name}.txt")

    # Resumo no stdout
    summary = {
        "total_logs": len(log_files),
        "total_findings": len(findings),
        "by_severity": {},
    }
    for f in findings:
        sev = f.get("severity", "desconhecido")
        summary["by_severity"][sev] = summary["by_severity"].get(sev, 0) + 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


