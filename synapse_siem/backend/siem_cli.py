#!/usr/bin/env python3
"""Shim de compatibilidade: delega execução para backend.main"""
from backend.main import main


if __name__ == "__main__":
    raise SystemExit(main())



