import itertools
import json
import logging

import requests

from filtros import PALAVRAS_TI

ENDPOINT = "https://mcp.pciconcursos.com.br/mcp"
TIMEOUT_SEGUNDOS = 20

_contador_id = itertools.count(1)


def chamar_mcp(nome_tool: str, argumentos: dict) -> list[dict]:
    payload = {
        "jsonrpc": "2.0",
        "id": next(_contador_id),
        "method": "tools/call",
        "params": {"name": nome_tool, "arguments": argumentos},
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }

    resposta = requests.post(ENDPOINT, json=payload, headers=headers, timeout=TIMEOUT_SEGUNDOS)
    resposta.raise_for_status()
    envelope = resposta.json()

    if "error" in envelope:
        raise RuntimeError(f"MCP retornou erro: {envelope['error']}")

    resultado = envelope["result"]
    conteudo = resultado["content"][0]["text"]

    if resultado.get("isError"):
        raise RuntimeError(f"MCP retornou isError=true para {nome_tool}({argumentos}): {conteudo}")

    corpo = json.loads(conteudo)

    if corpo.get("errors"):
        logging.warning("[PCI MCP] %s(%s) retornou erros: %s", nome_tool, argumentos, corpo["errors"])

    return corpo.get("data", [])


def coletar() -> list[dict]:
    itens: list[dict] = []

    for termo in PALAVRAS_TI:
        try:
            resultado = chamar_mcp("pesquisar_concursos", {"termo": termo, "uf": "pe"})
            logging.info("[PCI MCP] pesquisar_concursos(termo=%r, uf=pe) -> %d itens", termo, len(resultado))
            for item in resultado:
                item["_veio_de_busca_cidade"] = False
            itens.extend(resultado)
        except Exception:
            logging.exception("[PCI MCP] falhou ao buscar termo %r", termo)

    try:
        resultado = chamar_mcp("buscar_por_cidade", {"uf": "pe", "cidade": "Recife"})
        logging.info("[PCI MCP] buscar_por_cidade(uf=pe, cidade=Recife) -> %d itens", len(resultado))
        for item in resultado:
            item["_veio_de_busca_cidade"] = True
        itens.extend(resultado)
    except Exception:
        logging.exception("[PCI MCP] falhou ao buscar por cidade Recife")

    if not itens:
        logging.error("[PCI MCP] Nenhum item coletado em nenhuma chamada — verificar se o endpoint mudou")

    return itens
