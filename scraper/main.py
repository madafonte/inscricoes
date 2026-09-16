import logging

from filtros import detectar_escolaridade, detectar_localizacao, eh_relevante_ti
from modelos import Concurso
from sources.pci_mcp import coletar
from utils import agora_iso, carregar_json, configurar_logging, salvar_json

CAMINHO_DADOS = "data/concursos.json"


def montar_concurso(item: dict, localizacao: str, escolaridade: str, agora: str, antigos_por_id: dict) -> Concurso:
    id_ = item["id"]
    anterior = antigos_por_id.get(id_)
    datas = item.get("datas") or {}
    noticia = item.get("noticia") or {}

    return Concurso(
        id=id_,
        cargo=item.get("cargos_resumo") or ", ".join(item.get("cargos") or []) or item.get("titulo", ""),
        orgao=item.get("titulo", ""),
        data_limite=datas.get("fim"),
        dias_restantes=datas.get("dias_restantes"),
        localizacao=localizacao,
        escolaridade=escolaridade,
        fonte="pci_mcp",
        link=noticia.get("link", ""),
        titulo_bruto=noticia.get("titulo") or item.get("titulo", ""),
        vagas_salario=item.get("vagas_salario"),
        formacao_bruta=item.get("formacao"),
        primeira_vez_visto_em=anterior["primeira_vez_visto_em"] if anterior else agora,
        ultima_vez_visto_em=agora,
    )


def main() -> None:
    configurar_logging()
    agora = agora_iso()

    dados_antigos = carregar_json(CAMINHO_DADOS)
    antigos_por_id = {c["id"]: c for c in dados_antigos.get("concursos", [])}

    brutos = coletar()

    por_id: dict[int, dict] = {}
    flags_cidade: set[int] = set()
    for item in brutos:
        por_id[item["id"]] = item
        if item.get("_veio_de_busca_cidade"):
            flags_cidade.add(item["id"])

    finais: list[Concurso] = []
    descartados_localizacao = 0
    descartados_escolaridade = 0
    descartados_ti = 0

    for id_, item in por_id.items():
        cargos = item.get("cargos") or []
        titulo = item.get("titulo", "")

        if not eh_relevante_ti(cargos, titulo):
            descartados_ti += 1
            continue

        localizacao = detectar_localizacao(item, id_ in flags_cidade)
        if localizacao == "fora_de_escopo":
            descartados_localizacao += 1
            continue

        escolaridade = detectar_escolaridade(item.get("formacao", ""), cargos, titulo)
        if escolaridade == "excluir":
            descartados_escolaridade += 1
            continue

        finais.append(montar_concurso(item, localizacao, escolaridade, agora, antigos_por_id))

    logging.info(
        "Coleta finalizada: %d elegíveis de %d únicos (descartados: %d fora de TI, %d fora de Recife, %d escolaridade não elegível)",
        len(finais), len(por_id), descartados_ti, descartados_localizacao, descartados_escolaridade,
    )

    salvar_json(CAMINHO_DADOS, {
        "atualizado_em": agora,
        "concursos": [c.to_dict() for c in finais],
    })


if __name__ == "__main__":
    main()
