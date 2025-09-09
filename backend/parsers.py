import csv
import json
import re
from typing import Dict, Iterable, Iterator, Optional


APACHE_COMBINED_REGEX = re.compile(
    r"^(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] \"(?P<method>\S+) (?P<path>\S+) \S+\" (?P<status>\d{3}) (?P<size>\S+)( \"(?P<ref>[^\"]*)\" \"(?P<ua>[^\"]*)\")?"
)


def read_lines(path: str, max_lines: int = 0, encoding: str = "utf-8") -> Iterator[str]:
    count = 0
    with open(path, "r", encoding=encoding, errors="replace") as f:
        for line in f:
            if max_lines and count >= max_lines:
                break
            count += 1
            yield line.rstrip("\n")


def parse_jsonl(path: str, max_lines: int = 0, encoding: str = "utf-8") -> Iterator[Dict]:
    for line in read_lines(path, max_lines=max_lines, encoding=encoding):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                yield obj
        except json.JSONDecodeError:
            continue


def parse_json(path: str, max_lines: int = 0, encoding: str = "utf-8") -> Iterator[Dict]:
    try:
        with open(path, "r", encoding=encoding, errors="replace") as f:
            data = json.load(f)
        if isinstance(data, list):
            for i, item in enumerate(data):
                if max_lines and i >= max_lines:
                    break
                if isinstance(item, dict):
                    yield item
        elif isinstance(data, dict):
            yield data
    except Exception:
        return


def parse_csv(path: str, max_lines: int = 0, encoding: str = "utf-8") -> Iterator[Dict]:
    try:
        with open(path, newline="", encoding=encoding, errors="replace") as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                if max_lines and i >= max_lines:
                    break
                yield dict(row)
    except Exception:
        return


def parse_apache(path: str, max_lines: int = 0, encoding: str = "utf-8") -> Iterator[Dict]:
    for i, line in enumerate(read_lines(path, max_lines=max_lines, encoding=encoding)):
        m = APACHE_COMBINED_REGEX.match(line)
        if not m:
            continue
        d = m.groupdict()
        d["source"] = "apache"
        yield d


def parse_plaintext(path: str, max_lines: int = 0, encoding: str = "utf-8") -> Iterator[Dict]:
    for i, line in enumerate(read_lines(path, max_lines=max_lines, encoding=encoding)):
        yield {"message": line}


def autodetect_and_parse(path: str, max_lines: int = 0, encoding: str = "utf-8") -> Iterator[Dict]:
    lower = path.lower()
    if lower.endswith(".jsonl"):
        yield from parse_jsonl(path, max_lines=max_lines, encoding=encoding)
        return
    if lower.endswith(".json"):
        yield from parse_json(path, max_lines=max_lines, encoding=encoding)
        return
    if lower.endswith(".csv"):
        yield from parse_csv(path, max_lines=max_lines, encoding=encoding)
        return
    # tentativa simples de apache
    for line in read_lines(path, max_lines=10, encoding=encoding):
        if APACHE_COMBINED_REGEX.match(line):
            yield from parse_apache(path, max_lines=max_lines, encoding=encoding)
            return
        break
    # fallback
    yield from parse_plaintext(path, max_lines=max_lines, encoding=encoding)




