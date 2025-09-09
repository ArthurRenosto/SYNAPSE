import csv
import json
import os
from datetime import datetime
from typing import Dict, Iterable, List, Tuple


SEVERITY_ORDER = ["info", "low", "medium", "high", "critical"]
SEVERITY_LABEL = {
    "info": "Info",
    "low": "Baixa",
    "medium": "Média",
    "high": "Alta",
    "critical": "Crítica",
}
SEVERITY_EMOJI = {
    "info": "ℹ️",
    "low": "🟢",
    "medium": "🟡",
    "high": "🟠",
    "critical": "🔴",
}


def _summarize_by_severity(findings: List[Dict]) -> Dict[str, int]:
    summary: Dict[str, int] = {s: 0 for s in SEVERITY_ORDER}
    for f in findings:
        sev = f.get("severity", "medium")
        summary[sev] = summary.get(sev, 0) + 1
    return summary


def _aggregate_by_rule(findings: List[Dict]) -> List[Dict]:
    bucket: Dict[str, Dict] = {}
    for f in findings:
        rid = f.get("rule_id", "desconhecida")
        if rid not in bucket:
            bucket[rid] = {
                "rule_id": rid,
                "severity": f.get("severity", "medium"),
                "description": f.get("description", ""),
                "recommendation": f.get("recommendation", ""),
                "items": [],
                "per_file": {},
            }
        bucket[rid]["items"].append(f)
        src = f.get("source_file", "?")
        bucket[rid]["per_file"][src] = bucket[rid]["per_file"].get(src, 0) + 1
    groups = list(bucket.values())
    groups.sort(key=lambda g: (SEVERITY_ORDER.index(g.get("severity", "medium")), -len(g["items"])))
    return groups


class ReportWriter:
    def __init__(self, output_dir: str) -> None:
        self.output_dir = output_dir

    def write_json(self, findings: List[Dict], filename: str) -> str:
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(findings, f, ensure_ascii=False, indent=2)
        return path

    def write_csv(self, findings: List[Dict], filename: str) -> str:
        path = os.path.join(self.output_dir, filename)
        sources = sorted({item.get("source_file", "?") for item in findings})
        if not findings:
            with open(path, "w", newline="", encoding="utf-8") as f:
                # Cabeçalho informativo com arquivos analisados
                if sources:
                    f.write("# arquivos_analisados: " + " | ".join(sources) + "\n")
                writer = csv.writer(f)
                writer.writerow(["rule_id", "severity", "description", "source_file", "recommendation", "event"])
            return path
        keys = ["rule_id", "severity", "description", "source_file", "recommendation", "event"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            # Cabeçalho informativo com arquivos analisados
            if sources:
                f.write("# arquivos_analisados: " + " | ".join(sources) + "\n")
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for item in findings:
                row = {k: item.get(k) for k in keys}
                row["event"] = json.dumps(row.get("event", {}), ensure_ascii=False)
                writer.writerow(row)
        return path

    def write_markdown(self, findings: List[Dict], filename: str) -> str:
        path = os.path.join(self.output_dir, filename)
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sev_summary = _summarize_by_severity(findings)
        groups = _aggregate_by_rule(findings)
        total = len(findings)
        sources = sorted({item.get("source_file", "?") for item in findings})
        with open(path, "w", encoding="utf-8") as md:
            md.write("# Relatório de Análise de Logs - SYNAPSE\n\n")
            md.write(f"Gerado em: {generated_at}  \n")
            md.write(f"Total de ocorrências: **{total}**\n\n")
            if sources:
                md.write("Arquivos analisados:\n\n")
                for s in sources:
                    md.write(f"- `{s}`\n")
                md.write("\n")
            md.write("## Índice\n\n")
            md.write("- [Resumo por severidade](#resumo-por-severidade)\n")
            md.write("- [Principais regras](#principais-regras)\n")
            if groups:
                md.write("- [Detalhes por regra](#detalhes-por-regra)\n")
            md.write("\n")

            md.write("## Resumo por severidade\n\n")
            md.write("| Severidade | Ocorrências |\n|---|---:|\n")
            for s in reversed(SEVERITY_ORDER):
                count = sev_summary.get(s, 0)
                if count:
                    icon = SEVERITY_EMOJI.get(s, "")
                    md.write(f"| {icon} {SEVERITY_LABEL.get(s, s)} | {count} |\n")
            md.write("\n")

            md.write("## Principais regras\n\n")
            md.write("| Regra | Severidade | Ocorrências | Descrição |\n|---|---|---:|---|\n")
            for g in groups:
                icon = SEVERITY_EMOJI.get(g['severity'], "")
                md.write(f"| [`{g['rule_id']}`](#regra-{g['rule_id']}) | {icon} {SEVERITY_LABEL.get(g['severity'], g['severity'])} | {len(g['items'])} | {g['description']} |\n")
            md.write("\n")

            md.write("## Detalhes por regra\n\n")
            for g in groups:
                icon = SEVERITY_EMOJI.get(g['severity'], "")
                md.write(f"<a id=\"regra-{g['rule_id']}\"></a>\n")
                md.write(f"### {icon} `{g['rule_id']}` — {SEVERITY_LABEL.get(g['severity'], g['severity'])} ({len(g['items'])})\n\n")
                if g.get("description"):
                    md.write(f"{g['description']}\n\n")
                if g.get("recommendation"):
                    md.write(f"- **Recomendação**: {g['recommendation']}\n\n")
                if g.get("per_file"):
                    md.write("Arquivos afetados:\n\n")
                    md.write("| Arquivo | Ocorrências |\n|---|---:|\n")
                    for fname, cnt in sorted(g["per_file"].items(), key=lambda kv: kv[1], reverse=True):
                        md.write(f"| `{fname}` | {cnt} |\n")
                    md.write("\n")
                md.write("Exemplos de eventos (até 5):\n\n")
                for sample in g["items"][:5]:
                    pretty = json.dumps(sample.get("event", {}), ensure_ascii=False, indent=2)
                    md.write("```json\n")
                    md.write(pretty + "\n")
                    md.write("```\n\n")
        return path

    def write_html(self, findings: List[Dict], filename: str) -> str:
        path = os.path.join(self.output_dir, filename)
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sev_summary = _summarize_by_severity(findings)
        groups = _aggregate_by_rule(findings)
        total = len(findings)
        css = (
            "body{font-family:Segoe UI,Roboto,Arial,sans-serif;margin:20px;}"
            "h1{margin-bottom:0;} small{color:#555;} table{border-collapse:collapse;width:100%;}"
            "th,td{border:1px solid #ddd;padding:8px;} th{background:#f5f5f5;text-align:left;}"
            ".sev-info{background:#eef5ff;} .sev-low{background:#effaf0;} .sev-medium{background:#fff7e6;}"
            ".sev-high{background:#ffecec;} .sev-critical{background:#ffe1e1;} .badge{padding:2px 6px;border-radius:4px;}"
            ".b-info{background:#2f86eb;color:#fff;} .b-low{background:#2ecc71;color:#fff;} .b-medium{background:#f39c12;color:#fff;}"
            ".b-high{background:#e74c3c;color:#fff;} .b-critical{background:#c0392b;color:#fff;} pre{background:#f8f8f8;padding:8px;overflow:auto;}"
            "details{margin:8px 0;} summary{cursor:pointer;} .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:12px 0;}"
            ".card{border:1px solid #ddd;border-radius:8px;padding:12px;background:#fff;} .muted{color:#666;}"
            "#filter{padding:8px;border:1px solid #ccc;border-radius:6px;width:100%;max-width:420px;}"
        )
        def sev_class(sev: str) -> str:
            return {
                "info": "sev-info",
                "low": "sev-low",
                "medium": "sev-medium",
                "high": "sev-high",
                "critical": "sev-critical",
            }.get(sev, "")

        def badge(sev: str) -> str:
            label = SEVERITY_LABEL.get(sev, sev)
            cls = {
                "info": "b-info",
                "low": "b-low",
                "medium": "b-medium",
                "high": "b-high",
                "critical": "b-critical",
            }.get(sev, "b-medium")
            return f"<span class='badge {cls}'>{label}</span>"

        with open(path, "w", encoding="utf-8") as html:
            html.write("<!DOCTYPE html><html lang='pt-br'><head><meta charset='utf-8'>")
            html.write("<meta name='viewport' content='width=device-width, initial-scale=1'>")
            html.write("<title>Relatório de Análise de Logs - SYNAPSE</title>")
            html.write(f"<style>{css}</style></head><body>")
            html.write("<h1>Relatório de Análise de Logs - SYNAPSE</h1>")
            html.write(f"<small>Gerado em {generated_at}</small>")
            html.write(f"<p><strong>Total de ocorrências:</strong> {total}</p>")

            html.write("<h2>Resumo por severidade</h2>")
            html.write("<div class='grid'>")
            for s in reversed(SEVERITY_ORDER):
                count = sev_summary.get(s, 0)
                if count:
                    html.write(f"<div class='card {sev_class(s)}'><div>{badge(s)}</div><div style='font-size:28px;font-weight:700'>{count}</div><div class='muted'>ocorrências</div></div>")
            html.write("</div>")

            html.write("<h2>Principais regras</h2>")
            html.write("<input id='filter' type='search' placeholder='Filtrar por regra, severidade ou descrição...'>")
            html.write("<table id='rulesTbl'><thead><tr><th>Regra</th><th>Severidade</th><th>Ocorrências</th><th>Descrição</th></tr></thead><tbody>")
            for g in groups:
                html.write(
                    f"<tr class='{sev_class(g['severity'])}'><td><a href='#rule-{g['rule_id']}'><code>{g['rule_id']}</code></a></td><td>{badge(g['severity'])}</td><td>{len(g['items'])}</td><td>{g['description']}</td></tr>"
                )
            html.write("</tbody></table>")

            html.write("<h2>Detalhes por regra</h2>")
            for g in groups:
                html.write(f"<h3 id='rule-{g['rule_id']}'><code>{g['rule_id']}</code> — {badge(g['severity'])} ({len(g['items'])})</h3>")
                if g.get("description"):
                    html.write(f"<p>{g['description']}</p>")
                if g.get("recommendation"):
                    html.write(f"<p><strong>Recomendação:</strong> {g['recommendation']}</p>")
                if g.get("per_file"):
                    html.write("<h4>Arquivos afetados</h4>")
                    html.write("<table><thead><tr><th>Arquivo</th><th>Ocorrências</th></tr></thead><tbody>")
                    for fname, cnt in sorted(g["per_file"].items(), key=lambda kv: kv[1], reverse=True):
                        html.write(f"<tr><td><code>{fname}</code></td><td>{cnt}</td></tr>")
                    html.write("</tbody></table>")
                html.write("<h4>Exemplos (até 5)</h4>")
                for sample in g["items"][:5]:
                    pretty = json.dumps(sample.get("event", {}), ensure_ascii=False, indent=2)
                    html.write("<details><summary>Evento</summary>")
                    html.write(f"<pre>{pretty}</pre>")
                    html.write("</details>")
            html.write("<script>\nconst q=document.getElementById('filter');\nconst rows=[...document.querySelectorAll('#rulesTbl tbody tr')];\nq&&q.addEventListener('input',()=>{const v=q.value.toLowerCase();rows.forEach(r=>{r.style.display=r.innerText.toLowerCase().includes(v)?'':'none';});});\n</script>")
        return path

    def write_txt_simple(self, findings: List[Dict], filename: str) -> str:
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            sources = sorted({item.get("source_file", "?") for item in findings})
            if sources:
                f.write("arquivos_analisados:\n")
                for s in sources:
                    f.write(f"- {s}\n")
                f.write("\n")
            for item in findings:
                f.write(f"falha: {item.get('description','')}\n")
                f.write(f"severidade: {SEVERITY_LABEL.get(item.get('severity','medium'), item.get('severity','medium'))}\n")
                f.write(f"recomendacoes: {item.get('recommendation','')}\n")
                raw = item.get('raw_line')
                if not raw:
                    raw = json.dumps(item.get('event', {}), ensure_ascii=False)
                f.write(f"linha do log: {raw}\n\n")
                f.write("\n")
        return path




