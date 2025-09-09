import os
import json
from typing import Dict, Iterable, List

from .parsers import autodetect_and_parse
from .rules import Rule, load_rules_from_json


class LogAnalyzer:
    def __init__(self, rules_path: str, default_encoding: str = "utf-8") -> None:
        self.rules: List[Rule] = load_rules_from_json(rules_path)
        self.default_encoding = default_encoding

    def analyze_files(self, files: Iterable[str], max_lines: int = 0) -> List[Dict]:
        all_findings: List[Dict] = []
        for path in files:
            for event in autodetect_and_parse(path, max_lines=max_lines, encoding=self.default_encoding):
                findings = self._apply_rules(event, source_file=path)
                if findings:
                    all_findings.extend(findings)
        return all_findings

    def _apply_rules(self, event: Dict, source_file: str) -> List[Dict]:
        text_blob = " ".join(
            [
                str(v)
                for v in event.values()
                if isinstance(v, (str, int, float)) and v is not None
            ]
        )
        results: List[Dict] = []
        for rule in self.rules:
            if rule.pattern.search(text_blob):
                raw_line = None
                if isinstance(event.get("message"), str):
                    raw_line = event.get("message")
                else:
                    try:
                        raw_line = json.dumps(event, ensure_ascii=False)
                    except Exception:
                        raw_line = str(event)
                results.append(
                    {
                        "rule_id": rule.id,
                        "description": rule.description,
                        "severity": rule.severity,
                        "recommendation": rule.recommendation,
                        "source_file": source_file,
                        "event": event,
                        "raw_line": raw_line,
                    }
                )
        return results




