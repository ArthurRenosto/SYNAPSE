import json
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Pattern


SEVERITY_ORDER = ["info", "low", "medium", "high", "critical"]


@dataclass
class Rule:
    id: str
    description: str
    severity: str
    pattern: Pattern[str]
    recommendation: str


def load_rules_from_json(path: str) -> List[Rule]:
    if not os.path.exists(path):
        return default_rules()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    rules: List[Rule] = []
    for item in data:
        try:
            rules.append(
                Rule(
                    id=item["id"],
                    description=item["description"],
                    severity=item.get("severity", "medium"),
                    pattern=re.compile(item["regex"], re.IGNORECASE),
                    recommendation=item.get("recommendation", "Sem recomendação."),
                )
            )
        except Exception:
            continue
    return rules if rules else default_rules()


def default_rules() -> List[Rule]:
    return [
        Rule(
            id="RCE_SUSPECT",
            description="Possível tentativa de RCE (comandos perigosos)",
            severity="critical",
            pattern=re.compile(r"\b(wget|curl|nc|netcat|bash|sh|powershell)\b.*(http|https|\|\||;|&&)", re.IGNORECASE),
            recommendation="Bloquear IP de origem, revisar WAF/IDS, aplicar patches de input validation.",
        ),
        Rule(
            id="AUTH_FAILURE_BURST",
            description="Falhas de autenticação múltiplas",
            severity="high",
            pattern=re.compile(r"(failed password|authentication failure|invalid credentials)", re.IGNORECASE),
            recommendation="Habilitar lockout temporário, 2FA e alertas de brute force.",
        ),
        Rule(
            id="PERMISSION_DENIED",
            description="Erro de permissionamento (acesso negado)",
            severity="medium",
            pattern=re.compile(r"(permission denied|acesso negado|unauthorized|forbidden|403)" , re.IGNORECASE),
            recommendation="Revisar permissões de arquivos/ACLs e políticas de least privilege.",
        ),
        Rule(
            id="MALWARE_IOC",
            description="Indicador genérico de malware/IOC",
            severity="high",
            pattern=re.compile(r"(trojan|backdoor|malware|ransomware|c2|beacon)", re.IGNORECASE),
            recommendation="Isolar host, executar antivírus/EDR e caçar persistência.",
        ),
        Rule(
            id="SQLI",
            description="Possível SQL Injection",
            severity="high",
            pattern=re.compile(r"(union select|or 1=1|sleep\(\d+\)|xp_cmdshell)", re.IGNORECASE),
            recommendation="Sanitizar entradas, usar queries parametrizadas e WAF.",
        ),
    ]




