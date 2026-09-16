import json
import logging
import os
from datetime import datetime, timezone, timedelta

FUSO_RECIFE = timezone(timedelta(hours=-3))


def configurar_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def agora_iso() -> str:
    return datetime.now(FUSO_RECIFE).isoformat(timespec="seconds")


def carregar_json(caminho: str) -> dict:
    if not os.path.exists(caminho):
        return {"atualizado_em": None, "concursos": []}
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_json(caminho: str, dados: dict) -> None:
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
        f.write("\n")
