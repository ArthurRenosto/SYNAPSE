SYNAPSE - Analisador de Logs (SIEM simplificado)

Uso rápido:

```
python -m backend.main <arquivos_ou_diretorios> [--rules backend/rules.json] [--output-dir reports] [--formats json,md,csv,html,txt] [--max-lines 0] [--import-to DIR] [--import-only]

# modo interativo (sem argumentos):
python -m backend.main
> Informe os caminhos de logs (separados por espaço ou vírgula): logs/ access.log
```

Alternativa (a partir da raiz do projeto):

```
python backend/main.py <arquivos_ou_diretorios> --formats json,md,csv,html,txt
```

Exemplos:

```
# apenas analisar
python -m backend.main logs/ --formats json,md

# importar para uma pasta central e analisar
python -m backend.main logs/ --import-to imported_logs --formats json,csv,html

# apenas importar e sair
python -m backend.main access.log auth.log --import-to imported_logs --import-only
```

Recursos:
- Parsers: **JSON/JSONL**, **CSV**, **Apache Combined**, **texto puro** (fallback)
- Regras por `backend/rules.json` (ou padrão embutido)
- Relatórios em **JSON**, **CSV**, **Markdown**, **HTML** e **TXT** com severidade e recomendações

Estrutura:
- `backend/siem_cli.py`: CLI
- `backend/`: biblioteca com parsers, regras, análise e relatórios
- `backend/rules.json`: regras customizáveis
- `reports/`: saída dos relatórios

Requisitos:
- Python 3.9+
- (Opcional para o frontend) Django 5.2.6

Observações:
- Encoding padrão UTF-8 (ajuste via `--encoding`).
- `--max-lines` limita leitura por arquivo para testes rápidos.

